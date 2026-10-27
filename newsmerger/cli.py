from __future__ import annotations

import dataclasses
import functools
import json
import logging
import sys
from collections.abc import Callable, Iterable, Iterator
from contextlib import contextmanager
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

import click as plain_click
import rich_click
from foundation.clilib import (
    RICH_STDERR_DISABLED,
    RICH_STDOUT_DISABLED,
    RICH_STDOUT_ENABLED,
    click_logging_options,
    get_stderr_console,
    get_stdout_console,
)
from foundation.loglib import setup_logger_from_click
from foundation.plugin import PluginError
from foundation.storage import EntryNotFoundError
from rich.progress import Progress, SpinnerColumn, TextColumn, TimeElapsedColumn
from rich.syntax import Syntax
from rich.table import Table

from .app import Application, LockedError
from .config import DEFAULT_WORKFLOW, Config, ConfigError
from .consts import PACKAGE_NAME
from .db import (
    ANNOTATION_SORTS,
    ARTIFACT_SORTS,
    DELIVERY_SORTS,
    ITEM_SORTS,
    DeliveryStatus,
)
from .models import ProcessingScope, SourceItem
from .processors import RunSummary
from .sinks import SelectionRequiredError

# Help goes to stdout: rich only when stdout is a terminal.
click = plain_click if RICH_STDOUT_DISABLED else rich_click

LOGGER = logging.getLogger(PACKAGE_NAME)

# Errors a user can fix (bad config, unknown plugin...): reported without a traceback.
USER_ERRORS = (
    ConfigError,
    PluginError,
    LockedError,
    SelectionRequiredError,
)


def report_user_errors[**P, R](command: Callable[P, R]) -> Callable[P, R]:
    @functools.wraps(command)
    def wrapper(*args: P.args, **kwargs: P.kwargs) -> R:
        try:
            return command(*args, **kwargs)
        except USER_ERRORS as e:
            raise click.ClickException(str(e)) from e

    return wrapper


def setup_logging(log_options: dict[str, Any], default_log_level: str) -> None:
    """Configure the package logger from the global options, falling back to
    NEWSMERGER_LOG_LEVEL, then to `default_log_level`."""
    # Logs go through foundation's shared stderr console, the same one the
    # progress bars use, so live progress redraws around log records; plain
    # lines when stderr is not a terminal.
    setup_logger_from_click(
        PACKAGE_NAME, **log_options, default_log_level=default_log_level
    )


def app_from_context(ctx: click.Context, *, write: bool = False) -> Application:
    """Build the Application for this invocation and close it when the command
    ends. Commands that `write` hold the write lock until then.

    Logging is set up here, between loading the config, which may set its
    level, and building the Application, which already logs."""
    config_path = ctx.obj["config_path"]
    config = Config.from_file(config_path) if config_path else Config()
    setup_logging(ctx.obj["log_options"], config.log_level)
    app = Application(config)
    ctx.call_on_close(app.close)
    if write:
        app.lock()
    return app


@contextmanager
def progress_rows() -> Iterator[Progress]:
    """Phase and unit rows on stderr, off when stderr is not a terminal.

    stdout is not redirected through the live display, so tables still reach
    a redirected stdout; print them after the rows end, or they would break
    the redraw on a shared terminal."""
    progress = Progress(
        SpinnerColumn(finished_text="✔"),
        TextColumn("{task.description}"),
        TimeElapsedColumn(),
        console=get_stderr_console(),
        disable=RICH_STDERR_DISABLED,
        redirect_stdout=False,
    )
    with progress:
        yield progress


def run_each[T](
    progress: Progress, names: Iterable[str], run: Callable[[str], T]
) -> dict[str, T]:
    """Run each unit by name with its own row, removed when it ends."""
    results = {}
    for name in names:
        row = progress.add_task(name, total=None)
        try:
            results[name] = run(name)
        finally:
            progress.remove_task(row)
    return results


def print_table(title: str, headers: list[str], rows: list[list[Any]]) -> None:
    if RICH_STDOUT_DISABLED:
        print(title)
        for row in rows:
            print("\t".join(str(cell) for cell in row))
        return

    table = Table(title=title)
    for header in headers:
        table.add_column(header, overflow="fold")  # ids and URIs stay whole
    for row in rows:
        table.add_row(*(str(cell) for cell in row))
    get_stdout_console().print(table)


def scope_options[**P, R](command: Callable[P, R]) -> Callable[P, R]:
    """Add --source/--since/--until/--item/--limit, passed to the command as `scope`."""

    @click.option("--source", default=None, help="Limit to one source id")
    @click.option(
        "--since",
        type=click.DateTime(),
        default=None,
        help="Published at or after (UTC)",
    )
    @click.option(
        "--until", type=click.DateTime(), default=None, help="Published before (UTC)"
    )
    @click.option(
        "--item", "item_ids", type=int, multiple=True, help="Item id (repeatable)"
    )
    @click.option("--limit", type=int, default=None, help="At most this many items")
    @functools.wraps(command)
    def wrapper(
        *args: Any,
        source: str | None,
        since: datetime | None,
        until: datetime | None,
        item_ids: tuple[int, ...],
        limit: int | None,
        **kwargs: Any,
    ) -> R:
        scope = ProcessingScope(
            source=source,
            since=since.replace(tzinfo=UTC) if since else None,
            until=until.replace(tzinfo=UTC) if until else None,
            item_ids=item_ids or None,
            limit=limit,
        )
        return command(*args, scope=scope, **kwargs)

    return wrapper


def parse_artifact_ids(
    ctx: click.Context, param: click.Parameter, values: tuple[str, ...]
) -> tuple[tuple[str, str], ...]:
    """`<remixer>/<name>` values as pairs; the name may contain slashes."""
    pairs = []
    for value in values:
        remixer, _, name = value.partition("/")
        if not remixer or not name:
            raise click.BadParameter(f"'{value}' is not <remixer>/<name>")
        pairs.append((remixer, name))
    return tuple(pairs)


workflow_option = click.option(
    "-w",
    "--workflow",
    default=DEFAULT_WORKFLOW,
    show_default=True,
    help="The workflow to run",
)

artifact_ids_option = click.option(
    "--artifact",
    "artifact_ids",
    multiple=True,
    callback=parse_artifact_ids,
    help="Artifact as <remix key>/<name> (repeatable)",
)


@click.group()
@click.option("-c", "--config", "config_path", type=Path, default=None)
@click_logging_options
@click.pass_context
def cli(
    ctx: click.Context,
    config_path: Path | None,
    log_level: str | None,
    verbose: int,
    quiet: int,
) -> None:
    ctx.ensure_object(dict)
    ctx.obj["config_path"] = config_path
    ctx.obj["log_options"] = {
        "log_level": log_level,
        "verbose": verbose,
        "quiet": quiet,
    }


def import_sources(
    app: Application, progress: Progress, workflow: str
) -> list[list[Any]]:
    """Import every source of the workflow, a row each; return the summary
    rows (source, items, error)."""

    def import_one(source_id: str) -> list[Any]:
        try:
            items = app.import_source(source_id)
        except Exception as e:
            # One broken site must not stop the others; the summary reports it.
            LOGGER.exception(f"importing '{source_id}' failed")
            return [source_id, "-", f"{type(e).__name__}: {e}"]
        return [source_id, len(items), ""]

    sources = [source.id for source in app.sources(workflow)]
    return list(run_each(progress, sources, import_one).values())


def print_import(rows: list[list[Any]]) -> int:
    """Print the import summary; return how many sources failed."""
    print_table("Import", ["Source", "Items", "Error"], rows)
    return sum(1 for _, _, error in rows if error)


def print_process(summaries: dict[str, RunSummary]) -> int:
    """Print the process summary; return how many items failed."""
    print_table(
        "Process",
        ["Key", "Done", "Ignored", "Failed"],
        [[name, s.done, s.ignored, s.failed] for name, s in summaries.items()],
    )
    return sum(s.failed for s in summaries.values())


def print_remix(produced: dict[str, list[str]]) -> int:
    """Print the remix summary; remixers report no failures."""
    print_table(
        "Remix",
        ["Remix", "Artifacts"],
        [[name, ", ".join(names) or "-"] for name, names in produced.items()],
    )
    return 0


def print_deliver(summaries: dict[str, RunSummary]) -> int:
    """Print the deliver summary; return how many deliveries failed."""
    print_table(
        "Deliver",
        ["Delivery", "Delivered", "Failed"],
        [[name, s.done, s.failed] for name, s in summaries.items()],
    )
    return sum(s.failed for s in summaries.values())


@cli.command("import")
@workflow_option
@click.pass_context
@report_user_errors
def import_cmd(ctx: click.Context, workflow: str) -> None:
    """Import every source of the workflow."""
    app = app_from_context(ctx, write=True)
    with progress_rows() as progress:
        rows = import_sources(app, progress, workflow)
    if failed := print_import(rows):
        raise click.ClickException(f"{failed} source(s) failed")


@cli.command("process")
@click.argument("processor", required=False)
@workflow_option
@scope_options
@click.option(
    "--force",
    is_flag=True,
    help="Reprocess everything in scope, ignored items included, with fresh attempts",
)
@click.pass_context
@report_user_errors
def process_cmd(
    ctx: click.Context,
    processor: str | None,
    workflow: str,
    scope: ProcessingScope,
    force: bool,
) -> None:
    """Run every `process:` entry of the workflow in order, or only
    PROCESSOR's."""
    app = app_from_context(ctx, write=True)
    with progress_rows() as progress:
        summaries = run_each(
            progress,
            app.process_keys(processor, workflow=workflow),
            lambda key: app.run_process(
                key, workflow=workflow, scope=scope, force=force
            ),
        )
    print_process(summaries)


@cli.command("remix")
@click.argument("key", required=False)
@workflow_option
@scope_options
@click.pass_context
@report_user_errors
def remix_cmd(
    ctx: click.Context, key: str | None, workflow: str, scope: ProcessingScope
) -> None:
    """Run the `remix:` entry KEY, or every one of the workflow in order."""
    app = app_from_context(ctx, write=True)
    with progress_rows() as progress:
        produced = run_each(
            progress,
            [key] if key else app.remix_keys(workflow),
            lambda name: app.run_remix(name, scope=scope),
        )
    print_remix(produced)


@cli.command("deliver")
@click.argument("key", required=False)
@workflow_option
@scope_options
@artifact_ids_option
@click.option(
    "--requeue",
    is_flag=True,
    help="Requeue the failed deliveries in scope with fresh attempts",
)
@click.option(
    "--force",
    is_flag=True,
    help="Send the selected subjects now, whatever their state (needs KEY and"
    " --item or --artifact)",
)
@click.pass_context
@report_user_errors
def deliver_cmd(
    ctx: click.Context,
    key: str | None,
    workflow: str,
    scope: ProcessingScope,
    artifact_ids: tuple[tuple[str, str], ...],
    requeue: bool,
    force: bool,
) -> None:
    """Run the workflow's `deliver:` entry KEY, or every one in order.

    Without --since or --item, an entry queues what is new in its lookback
    window, then delivers what is due.
    """
    if force and key is None:
        raise click.UsageError("--force needs a KEY")
    app = app_from_context(ctx, write=True)
    with progress_rows() as progress:
        summaries = run_each(
            progress,
            [key] if key else app.delivery_keys(workflow),
            lambda name: app.run_delivery(
                name,
                workflow=workflow,
                scope=scope,
                artifacts=artifact_ids,
                requeue=requeue,
                force=force,
            ),
        )
    print_deliver(summaries)


@cli.command("run")
@workflow_option
@click.pass_context
@report_user_errors
def run_cmd(ctx: click.Context, workflow: str) -> None:
    """Run the workflow's import, process, remix and deliver in turn.

    A failure is logged and the next phase still runs; the exit status is
    non-zero if anything failed.
    """
    app = app_from_context(ctx, write=True)
    failures = 0

    # (phase, run under the progress rows, print its summary and count failures)
    phases: list[tuple[str, Callable[[Progress], Any], Callable[[Any], int]]] = [
        (
            "import",
            lambda progress: import_sources(app, progress, workflow),
            print_import,
        ),
        (
            "process",
            lambda progress: run_each(
                progress,
                app.process_keys(workflow=workflow),
                lambda key: app.run_process(key, workflow=workflow),
            ),
            print_process,
        ),
        (
            "remix",
            lambda progress: run_each(
                progress, app.remix_keys(workflow), app.run_remix
            ),
            print_remix,
        ),
        (
            "deliver",
            lambda progress: run_each(
                progress,
                app.delivery_keys(workflow),
                lambda key: app.run_delivery(key, workflow=workflow),
            ),
            print_deliver,
        ),
    ]
    results = []
    with progress_rows() as progress:
        for number, (phase, run_phase, print_summary) in enumerate(phases, start=1):
            description = f"{phase} ({number}/{len(phases)})"
            row = progress.add_task(description, total=1)
            try:
                results.append((print_summary, run_phase(progress)))
            except Exception:
                LOGGER.exception(f"{phase} failed")
                failures += 1
                progress.update(row, description=f"{description} failed")
            progress.update(row, completed=1)

    for print_summary, result in results:
        failures += print_summary(result)
    if failures:
        raise click.ClickException(f"{failures} failure(s); see the log above")


def match_snippet(text: str, query: str, width: int = 60) -> str | None:
    """The text around the first case-insensitive match, on one line."""
    start = text.casefold().find(query.casefold())
    if start < 0:
        return None
    snippet = text[max(start - width, 0) : start + len(query) + width]
    return " ".join(snippet.split())


@cli.command("search")
@click.argument("query")
@scope_options
@click.pass_context
@report_user_errors
def search_cmd(ctx: click.Context, query: str, scope: ProcessingScope) -> None:
    """Items whose markdownify text contains QUERY (case-insensitive).

    --limit counts the items searched, not the matches.
    """
    app = app_from_context(ctx)
    items = app.get_items(scope)
    # shortcut: loads every markdown from disk, add an index if it gets slow
    markdowns = app.get_annotation_values(items, key="markdown")
    rows = []
    for item in items:
        snippet = match_snippet(markdowns.get(item.key, ""), query)
        if snippet is not None:
            rows.append([item.id, item.source.id, item.title, snippet])
    print_table("Matches", ["ID", "Source", "Title", "Match"], rows)


@cli.group("deliveries")
def deliveries_group() -> None:
    """Settle the delivery ledger (read it with `inspect deliveries`)."""


@deliveries_group.command("resolve")
@click.argument("sink", metavar="LEDGER_KEY")
@click.option(
    "--as",
    "status",
    type=click.Choice([DeliveryStatus.DONE.value, DeliveryStatus.QUEUED.value]),
    required=True,
    help="done: it was delivered; queued: deliver it again",
)
@scope_options
@artifact_ids_option
@click.pass_context
@report_user_errors
def resolve_cmd(
    ctx: click.Context,
    sink: str,
    status: str,
    scope: ProcessingScope,
    artifact_ids: tuple[tuple[str, str], ...],
) -> None:
    """Settle the interrupted (`sending`) deliveries of LEDGER_KEY (as
    `inspect deliveries` shows it) in the selection."""
    resolved = app_from_context(ctx, write=True).resolve_deliveries(
        sink,
        DeliveryStatus(status),
        scope=scope,
        artifact_names=artifact_ids or None,
    )
    click.echo(f"Resolved {resolved} interrupted delivery(ies) of '{sink}' as {status}")


# --- Inspection -------------------------------------------------------------

PREVIEW_LENGTH = 80


def format_value(value: Any) -> str:
    """An annotation value as text: strings as they are, the rest as JSON."""
    if isinstance(value, str):
        return value
    return json.dumps(value, indent=2, ensure_ascii=False, default=str)


def preview(value: Any) -> str:
    """One line of the value: the first line of text, or compact JSON."""
    if isinstance(value, str):
        lines = value.splitlines()
    else:
        lines = [json.dumps(value, ensure_ascii=False, default=str)]
    first = lines[0] if lines else ""
    if len(lines) > 1 or len(first) > PREVIEW_LENGTH:
        return first[: PREVIEW_LENGTH - 1] + "…"
    return first


def lexer_for(content_type: str) -> str | None:
    for marker in ("json", "xml", "html"):
        if marker in content_type:
            return marker
    return None


def json_default(value: Any) -> str:
    return value.isoformat() if isinstance(value, datetime) else str(value)


def print_json(records: list[dict[str, Any]]) -> None:
    click.echo(json.dumps(records, indent=2, ensure_ascii=False, default=json_default))


def check_found(kind: str, requested: Iterable[Any], found: Iterable[Any]) -> None:
    """Fail on explicitly requested ids the selection did not return."""
    if missing := set(requested) - set(found):
        listed = ", ".join(sorted(str(id_) for id_ in missing))
        raise click.ClickException(f"no {kind} {listed} in the selection")


processor_option = click.option(
    "--processor", default=None, help="Only this processor's annotations"
)


def annotation_options[**P, R](command: Callable[P, R]) -> Callable[P, R]:
    """Add --processor/--key/--annotation, which narrow an item selection."""
    command = click.option(
        "--annotation",
        "annotation_ids",
        type=int,
        multiple=True,
        help="Annotation id (repeatable)",
    )(command)
    command = click.option("--key", default=None, help="Only this key")(command)
    return processor_option(command)


def artifact_options[**P, R](command: Callable[P, R]) -> Callable[P, R]:
    """Add --remixer/--artifact/--limit, which select artifacts."""
    command = click.option(
        "--limit", type=int, default=None, help="At most this many artifacts"
    )(command)
    command = artifact_ids_option(command)
    return click.option(
        "--remixer", default=None, help="Only this remix key's artifacts"
    )(command)


def sort_option(keys: Iterable[str]) -> Callable[[Callable], Callable]:
    """--sort among `keys`, oldest (or smallest) first; `updated` by default.
    It also decides which rows --limit keeps."""
    return click.option(
        "--sort",
        type=click.Choice(sorted(keys)),
        default="updated",
        show_default=True,
        help="Sort key, ascending (oldest first for dates)",
    )


format_option = click.option(
    "--format",
    "output_format",
    type=click.Choice(["table", "json"]),
    default="table",
    help="Output format",
)


def print_content(content: str, content_type: str) -> None:
    """Content to stdout as is, highlighted on a terminal."""
    lexer = lexer_for(content_type)
    if RICH_STDOUT_ENABLED and lexer:
        get_stdout_console().print(Syntax(content, lexer))
    else:
        sys.stdout.write(content)


@cli.group("inspect")
def inspect_group() -> None:
    """Show what is stored (read-only)."""


def print_item(item: SourceItem, annotations: list[tuple[int, str, str]]) -> None:
    """One item as field/value rows, one row per annotation."""
    dates = (item.published_at, item.modified_at)
    published, modified = (f"{d:%Y-%m-%d %H:%M}" if d else "" for d in dates)
    print_table(
        f"Item {item.id}",
        ["Field", "Value"],
        [
            ["Source", item.source.id],
            ["UID", item.uid],
            ["Title", item.title],
            ["URI", item.uri],
            ["Published", published],
            ["Modified", modified],
            ["Mimetype", item.mimetype],
            ["Content", f"inspect content --sha256 {item.content_sha256}"],
            ["Data", format_value(item.data)],
            *(
                [f"Annotation #{annotation_id}", f"{processor}.{key}"]
                for annotation_id, processor, key in annotations
            ),
        ],
    )


@inspect_group.command("items")
@scope_options
@sort_option(ITEM_SORTS)
@format_option
@click.pass_context
@report_user_errors
def inspect_items_cmd(
    ctx: click.Context, scope: ProcessingScope, sort: str, output_format: str
) -> None:
    """Items in scope, with the ids and keys of their annotations.

    One --item in table format shows all its fields, one row per annotation.
    """
    app = app_from_context(ctx)
    items = app.get_items(scope, sort=sort)
    if scope.limit is None:  # with a limit, a requested item may just be cut off
        check_found("item", scope.item_ids or (), (item.id for item in items))
    annotations = app.get_annotation_keys(item.id for item in items)

    if output_format == "json":
        print_json(
            [
                {
                    "id": item.id,
                    "source": item.source.id,
                    "uid": item.uid,
                    "title": item.title,
                    "uri": item.uri,
                    "mimetype": item.mimetype,
                    "content_sha256": item.content_sha256,
                    "data": item.data,
                    "published_at": item.published_at,
                    "modified_at": item.modified_at,
                    "annotations": [
                        {"id": annotation_id, "processor": processor, "key": key}
                        for annotation_id, processor, key in annotations.get(
                            item.id, []
                        )
                    ],
                }
                for item in items
            ]
        )
        return

    if len(scope.item_ids or ()) == 1 and items:
        print_item(items[0], annotations.get(items[0].id, []))
        return

    print_table(
        "Items",
        ["ID", "Source", "Published", "Title", "Annotations"],
        [
            [
                item.id,
                item.source.id,
                f"{item.published_at:%Y-%m-%d %H:%M}",
                item.title,
                "\n".join(
                    f"{annotation_id} {processor}.{key}"
                    for annotation_id, processor, key in annotations.get(item.id, [])
                ),
            ]
            for item in items
        ],
    )


@inspect_group.command("annotations")
@scope_options
@annotation_options
@sort_option(ANNOTATION_SORTS)
@format_option
@click.pass_context
@report_user_errors
def inspect_annotations_cmd(
    ctx: click.Context,
    scope: ProcessingScope,
    processor: str | None,
    key: str | None,
    annotation_ids: tuple[int, ...],
    sort: str,
    output_format: str,
) -> None:
    """Annotations of the items in scope; --limit counts annotations.

    One --annotation in table format prints its full value (text as is, the
    rest as JSON) to stdout and its metadata to stderr.
    """
    annotations = app_from_context(ctx).find_annotations(
        scope,
        processor=processor,
        key=key,
        annotation_ids=annotation_ids or None,
        sort=sort,
    )
    if scope.limit is None:
        check_found("annotation", annotation_ids, (a.id for a in annotations))

    if output_format == "json":
        print_json([dataclasses.asdict(annotation) for annotation in annotations])
    elif len(annotation_ids) == 1:
        (annotation,) = annotations
        click.echo(
            f"{annotation.id} · item {annotation.item_id} · "
            f"{annotation.processor}.{annotation.key} · "
            f"updated {annotation.updated_at:%Y-%m-%d %H:%M}",
            err=True,
        )
        click.echo(format_value(annotation.value))
    else:
        print_table(
            "Annotations",
            ["ID", "Item", "Processor.Key", "Updated", "Value"],
            [
                [
                    a.id,
                    a.item_id,
                    f"{a.processor}.{a.key}",
                    f"{a.updated_at:%Y-%m-%d %H:%M}",
                    preview(a.value),
                ]
                for a in annotations
            ],
        )


@inspect_group.command("artifacts")
@artifact_options
@sort_option(ARTIFACT_SORTS)
@format_option
@click.pass_context
@report_user_errors
def inspect_artifacts_cmd(
    ctx: click.Context,
    remixer: str | None,
    artifact_ids: tuple[tuple[str, str], ...],
    limit: int | None,
    sort: str,
    output_format: str,
) -> None:
    """Stored artifacts. Contents are loaded only for --artifact.

    One --artifact in table format prints its content to stdout and its
    metadata to stderr, so it can be redirected.
    """
    app = app_from_context(ctx)
    artifacts = app.list_artifacts(
        remixer, names=artifact_ids or None, limit=limit, sort=sort
    )
    if limit is None:
        check_found(
            "artifact",
            (f"{r}/{n}" for r, n in artifact_ids),
            (f"{a.remixer}/{a.name}" for a in artifacts),
        )
    if artifact_ids:
        artifacts = [app.get_artifact(a.remixer, a.name) for a in artifacts]

    if output_format == "json":
        records = []
        for artifact in artifacts:
            record = {
                "id": f"{artifact.remixer}/{artifact.name}",
                "remixer": artifact.remixer,
                "name": artifact.name,
                "content_type": artifact.content_type,
                "created_at": artifact.created_at,
                "updated_at": artifact.updated_at,
            }
            if artifact_ids:
                record["content"] = artifact.content
            records.append(record)
        print_json(records)
    elif len(artifact_ids) == 1:
        (artifact,) = artifacts
        click.echo(
            f"{artifact.remixer}/{artifact.name} · {artifact.content_type} · "
            f"updated {artifact.updated_at:%Y-%m-%d %H:%M}",
            err=True,
        )
        print_content(artifact.content, artifact.content_type)
    else:
        print_table(
            "Artifacts",
            ["ID", "Type", "Updated"],
            [
                [
                    f"{a.remixer}/{a.name}",
                    a.content_type,
                    f"{a.updated_at:%Y-%m-%d %H:%M}",
                ]
                for a in artifacts
            ],
        )


@inspect_group.command("content")
@click.option("--sha256", required=True, help="The content's sha256")
@click.pass_context
@report_user_errors
def inspect_content_cmd(ctx: click.Context, sha256: str) -> None:
    """Stored content (of an item, annotation or artifact) as is, to stdout."""
    try:
        content = app_from_context(ctx).get_stored_content(sha256)
    except EntryNotFoundError as e:
        raise click.ClickException(f"no content {sha256}") from e
    click.echo(content, nl=False)


@inspect_group.command("deliveries")
@scope_options
@artifact_ids_option
@click.option("--sink", default=None, help="Only this ledger key's deliveries")
@click.option(
    "--status",
    type=click.Choice([status.value for status in DeliveryStatus]),
    default=None,
    help="Only deliveries in this state",
)
@sort_option(DELIVERY_SORTS)
@format_option
@click.pass_context
@report_user_errors
def inspect_deliveries_cmd(
    ctx: click.Context,
    scope: ProcessingScope,
    artifact_ids: tuple[tuple[str, str], ...],
    sink: str | None,
    status: str | None,
    sort: str,
    output_format: str,
) -> None:
    """The delivery ledger; --limit counts rows.

    Item filters keep item deliveries, --artifact artifact deliveries.
    """
    deliveries = app_from_context(ctx).find_deliveries(
        scope,
        sink=sink,
        status=DeliveryStatus(status) if status else None,
        artifact_names=artifact_ids or None,
        sort=sort,
    )

    if output_format == "json":
        print_json([dataclasses.asdict(delivery) for delivery in deliveries])
        return

    print_table(
        "Deliveries",
        ["Sink", "Subject", "Status", "Attempts", "Updated", "Error"],
        [
            [
                d.sink,
                f"item {d.item_id}" if d.item_id is not None else d.artifact_name,
                d.status,
                d.attempts,
                f"{d.updated_at:%Y-%m-%d %H:%M}",
                preview(d.last_error or ""),
            ]
            for d in deliveries
        ],
    )


# --- Deletion ---------------------------------------------------------------

force_delete_option = click.option(
    "--force",
    is_flag=True,
    help="Also delete what has deliveries, and their ledger rows, so it can be"
    " delivered again",
)


def require_selection(*filters: object) -> None:
    """Refuse a selection that names no filter or id: it would match all."""
    if not any(filters):
        raise click.UsageError("name a filter or an id to select what to delete")


@cli.group("delete")
def delete_group() -> None:
    """Delete stored data, without asking. `inspect` with the same options
    lists what would be deleted."""


@delete_group.command("items")
@scope_options
@sort_option(ITEM_SORTS)
@force_delete_option
@click.pass_context
@report_user_errors
def delete_items_cmd(
    ctx: click.Context, scope: ProcessingScope, sort: str, force: bool
) -> None:
    """Delete items with their processing state, annotations and deliveries.

    Items with deliveries are skipped unless --force. An item still in its
    source's index comes back on the next import, with a new id.
    """
    require_selection(scope.source, scope.since, scope.until, scope.item_ids)
    app = app_from_context(ctx, write=True)
    items = app.get_items(scope, sort=sort)
    if scope.limit is None:
        check_found("item", scope.item_ids or (), (item.id for item in items))

    delivered: set[int | None] = set()
    if items and not force:
        selected = ProcessingScope(item_ids=tuple(item.id for item in items))
        delivered = {d.item_id for d in app.find_deliveries(selected)}
        for item_id in sorted(delivered):
            click.echo(f"Skipped item {item_id}: it has deliveries (--force)", err=True)

    deleted = app.delete_items(item.id for item in items if item.id not in delivered)
    click.echo(f"Deleted {deleted} item(s)")


@delete_group.command("annotations")
@scope_options
@processor_option
@sort_option(ANNOTATION_SORTS)
@click.pass_context
@report_user_errors
def delete_annotations_cmd(
    ctx: click.Context, scope: ProcessingScope, processor: str | None, sort: str
) -> None:
    """Delete annotations per processor: every key it wrote on the item,
    with their processing state, so the item becomes pending again for each
    of its runs.

    --limit is refused: it counts annotations, not processors.
    """
    if scope.limit is not None:
        raise click.UsageError(
            "--limit counts annotations, but they are deleted per processor"
        )
    require_selection(scope.source, scope.since, scope.until, scope.item_ids, processor)
    app = app_from_context(ctx, write=True)
    annotations = app.find_annotations(scope, processor=processor, sort=sort)

    targets = sorted({(a.item_id, a.processor) for a in annotations})
    deleted = sum(
        app.delete_annotations(processor=target, item_id=item_id)
        for item_id, target in targets
    )
    click.echo(
        f"Deleted {deleted} annotation(s); {len(targets)} (item, processor)"
        " pair(s) are pending again"
    )


@delete_group.command("artifacts")
@artifact_options
@sort_option(ARTIFACT_SORTS)
@force_delete_option
@click.pass_context
@report_user_errors
def delete_artifacts_cmd(
    ctx: click.Context,
    remixer: str | None,
    artifact_ids: tuple[tuple[str, str], ...],
    limit: int | None,
    sort: str,
    force: bool,
) -> None:
    """Delete artifacts with their deliveries; the next run of their
    remixer rebuilds them.

    Artifacts with deliveries are skipped unless --force.
    """
    require_selection(remixer, artifact_ids)
    app = app_from_context(ctx, write=True)
    artifacts = app.list_artifacts(
        remixer, names=artifact_ids or None, limit=limit, sort=sort
    )
    if limit is None:
        check_found(
            "artifact",
            (f"{r}/{n}" for r, n in artifact_ids),
            (f"{a.remixer}/{a.name}" for a in artifacts),
        )

    delivered: set[str | None] = set()
    if artifacts and not force:
        delivered = {
            d.artifact_name
            for d in app.find_deliveries(
                artifact_names=[(a.remixer, a.name) for a in artifacts]
            )
        }
        for name in sorted(n for n in delivered if n is not None):
            click.echo(
                f"Skipped artifact {name}: it has deliveries (--force)", err=True
            )

    deleted = app.delete_artifacts(
        (a.remixer, a.name)
        for a in artifacts
        if f"{a.remixer}/{a.name}" not in delivered
    )
    click.echo(f"Deleted {deleted} artifact(s)")
