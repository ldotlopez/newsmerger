from __future__ import annotations

import dataclasses
import functools
import json
import logging
import sys
from collections.abc import Callable, Iterable
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

import click as plain_click
import rich_click
from foundation.clilib import (
    RICH_DISABLED,
    RICH_ENABLED,
    click_logging_options,
    get_stderr_console,
    get_stdout_console,
)
from foundation.loglib import setup_logger_from_click
from foundation.plugin import PluginError
from rich.progress import track
from rich.syntax import Syntax
from rich.table import Table

from .app import Application, UnsupportedProviderError
from .config import ConfigError
from .consts import PACKAGE_NAME
from .models import ProcessingScope

click = plain_click if RICH_DISABLED else rich_click

LOGGER = logging.getLogger(PACKAGE_NAME)

# Errors a user can fix (bad config, unknown plugin...): reported without a traceback.
USER_ERRORS = (ConfigError, PluginError, UnsupportedProviderError)


def report_user_errors[**P, R](command: Callable[P, R]) -> Callable[P, R]:
    @functools.wraps(command)
    def wrapper(*args: P.args, **kwargs: P.kwargs) -> R:
        try:
            return command(*args, **kwargs)
        except USER_ERRORS as e:
            raise click.ClickException(str(e)) from e

    return wrapper


def app_from_context(ctx: click.Context) -> Application:
    """Build the Application for this invocation and close it when the command ends."""
    app = Application.from_config_file(ctx.obj["config_path"])
    ctx.call_on_close(app.close)
    return app


def print_table(title: str, headers: list[str], rows: list[list[Any]]) -> None:
    if RICH_DISABLED:
        print(title)
        for row in rows:
            print("\t".join(str(cell) for cell in row))
        return

    table = Table(title=title)
    for header in headers:
        table.add_column(header)
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


@click.group()
@click.option("-c", "--config", "config_path", type=Path, default=None)
@click_logging_options
@click.pass_context
def cli(
    ctx: click.Context,
    config_path: Path | None,
    log_level: str,
    verbose: int,
    quiet: int,
) -> None:
    # Logs go through foundation's shared stderr console, the same one the
    # progress bars use, so live progress redraws around log records.
    logger = setup_logger_from_click(
        PACKAGE_NAME,
        log_level=log_level,
        verbose=verbose,
        quiet=quiet,
        infect=RICH_ENABLED,
    )
    if RICH_DISABLED:
        handler = logging.StreamHandler()
        handler.setFormatter(
            logging.Formatter("%(asctime)s %(levelname)s %(name)s: %(message)s")
        )
        logger.addHandler(handler)
    ctx.ensure_object(dict)
    ctx.obj["config_path"] = config_path


@cli.command("import")
@click.pass_context
@report_user_errors
def import_cmd(ctx: click.Context) -> None:
    """Import every configured source."""
    app = app_from_context(ctx)

    rows = []
    failed = 0
    for source in track(
        app.sources,
        description="Importing",
        console=get_stderr_console(),
        disable=RICH_DISABLED,
    ):
        try:
            items = app.import_source(source.id)
        except Exception as e:
            # One broken site must not stop the others; the summary reports it.
            LOGGER.exception(f"importing '{source.id}' failed")
            rows.append([source.id, "-", f"{type(e).__name__}: {e}"])
            failed += 1
        else:
            rows.append([source.id, len(items), ""])

    print_table("Import", ["Source", "Items", "Error"], rows)
    if failed:
        raise click.ClickException(f"{failed} source(s) failed")


@cli.command("import-url")
@click.option("--source", "source_id", required=True, help="Configured source id")
@click.argument("url")
@click.pass_context
@report_user_errors
def import_url_cmd(ctx: click.Context, source_id: str, url: str) -> None:
    """Import one article URL into a configured source."""
    item = app_from_context(ctx).import_url(source_id, url)
    click.echo(f"Imported '{item.title}' from {item.uri}")


@cli.command("enrich")
@click.argument("processor", required=False)
@scope_options
@click.option(
    "--force",
    is_flag=True,
    help="Reprocess everything in scope, ignored items included, with fresh attempts",
)
@click.pass_context
@report_user_errors
def enrich_cmd(
    ctx: click.Context, processor: str | None, scope: ProcessingScope, force: bool
) -> None:
    """Run one processor, or every configured one in order."""
    app = app_from_context(ctx)
    if processor:
        summaries = {processor: app.run_processor(processor, scope=scope, force=force)}
    else:
        summaries = app.enrich(scope=scope, force=force)

    print_table(
        "Enrich",
        ["Processor", "Done", "Ignored", "Failed"],
        [[name, s.done, s.ignored, s.failed] for name, s in summaries.items()],
    )


@cli.command("remix")
@click.argument("remixer", required=False)
@scope_options
@click.pass_context
@report_user_errors
def remix_cmd(ctx: click.Context, remixer: str | None, scope: ProcessingScope) -> None:
    """Run one remixer, or every configured one in order."""
    app = app_from_context(ctx)
    if remixer:
        produced = {remixer: app.run_remixer(remixer, scope=scope)}
    else:
        produced = app.remix(scope=scope)

    print_table(
        "Remix",
        ["Remixer", "Artifacts"],
        [[name, ", ".join(names) or "-"] for name, names in produced.items()],
    )


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
    return click.option(
        "--processor", default=None, help="Only this processor's annotations"
    )(command)


def artifact_options[**P, R](command: Callable[P, R]) -> Callable[P, R]:
    """Add --remixer/--artifact/--limit, which select artifacts."""
    command = click.option(
        "--limit", type=int, default=None, help="At most this many artifacts"
    )(command)
    command = click.option(
        "--artifact",
        "artifact_ids",
        multiple=True,
        callback=parse_artifact_ids,
        help="Artifact as <remixer>/<name> (repeatable)",
    )(command)
    return click.option(
        "--remixer", default=None, help="Only this remixer's artifacts"
    )(command)


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
    if RICH_ENABLED and lexer and sys.stdout.isatty():
        get_stdout_console().print(Syntax(content, lexer))
    else:
        sys.stdout.write(content)


@cli.group("inspect")
def inspect_group() -> None:
    """Show what is stored (read-only)."""


@inspect_group.command("items")
@scope_options
@format_option
@click.pass_context
@report_user_errors
def inspect_items_cmd(
    ctx: click.Context, scope: ProcessingScope, output_format: str
) -> None:
    """Items in scope, oldest first, with the ids and keys of their annotations."""
    app = app_from_context(ctx)
    items = app.get_items(scope)
    if scope.limit is None:  # with a limit, a requested item may just be cut off
        check_found("item", scope.item_ids or (), (item.id for item in items))
    annotations = app.get_annotation_keys(items)

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

    print_table(
        "Items",
        ["ID", "Source", "Published", "Title", "Annotations"],
        [
            [
                item.id,
                item.source.id,
                f"{item.published_at:%Y-%m-%d %H:%M}",
                item.title,
                ", ".join(
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
@format_option
@click.pass_context
@report_user_errors
def inspect_annotations_cmd(
    ctx: click.Context,
    scope: ProcessingScope,
    processor: str | None,
    key: str | None,
    annotation_ids: tuple[int, ...],
    output_format: str,
) -> None:
    """Annotations of the items in scope; --limit counts annotations.

    One --annotation in table format prints its full value (text as is, the
    rest as JSON) to stdout and its metadata to stderr.
    """
    annotations = app_from_context(ctx).find_annotations(
        scope, processor=processor, key=key, annotation_ids=annotation_ids or None
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
@format_option
@click.pass_context
@report_user_errors
def inspect_artifacts_cmd(
    ctx: click.Context,
    remixer: str | None,
    artifact_ids: tuple[tuple[str, str], ...],
    limit: int | None,
    output_format: str,
) -> None:
    """Artifacts by remixer and name. Contents are loaded only for --artifact.

    One --artifact in table format prints its content to stdout and its
    metadata to stderr, so it can be redirected.
    """
    app = app_from_context(ctx)
    artifacts = app.list_artifacts(remixer, names=artifact_ids or None, limit=limit)
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
