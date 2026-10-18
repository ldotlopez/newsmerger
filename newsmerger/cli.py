from __future__ import annotations

import functools
import json
import logging
import sys
from collections.abc import Callable
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

import click as plain_click
import rich_click
from foundation.loglib import setup_logger
from foundation.plugin import PluginError
from rich.console import Console
from rich.progress import track
from rich.syntax import Syntax
from rich.table import Table

from .app import Application, UnsupportedProviderError
from .config import ConfigError
from .consts import DISABLE_RICH, PACKAGE_NAME
from .models import ProcessingScope, SourceItem

click = plain_click if DISABLE_RICH else rich_click

LOGGER = logging.getLogger(PACKAGE_NAME)

console = Console(no_color=DISABLE_RICH, highlight=not DISABLE_RICH)

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
    if DISABLE_RICH:
        print(title)
        for row in rows:
            print("\t".join(str(cell) for cell in row))
        return

    table = Table(title=title)
    for header in headers:
        table.add_column(header)
    for row in rows:
        table.add_row(*(str(cell) for cell in row))
    console.print(table)


def scope_options[**P, R](command: Callable[P, R]) -> Callable[P, R]:
    """Add --source/--since/--until/--limit, passed to the command as `scope`."""

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
    @click.option("--limit", type=int, default=None, help="At most this many items")
    @functools.wraps(command)
    def wrapper(
        *args: Any,
        source: str | None,
        since: datetime | None,
        until: datetime | None,
        limit: int | None,
        **kwargs: Any,
    ) -> R:
        scope = ProcessingScope(
            source=source,
            since=since.replace(tzinfo=UTC) if since else None,
            until=until.replace(tzinfo=UTC) if until else None,
            limit=limit,
        )
        return command(*args, scope=scope, **kwargs)

    return wrapper


@click.group()
@click.option("-c", "--config", "config_path", type=Path, default=None)
@click.option(
    "--log-level",
    default="info",
    show_default=True,
    help="Level name, or a foundation.loglib spec such as 'info,db:debug'",
)
@click.option("-v", "--verbose", is_flag=True, help="Shortcut for --log-level debug")
@click.pass_context
def cli(
    ctx: click.Context, config_path: Path | None, log_level: str, verbose: bool
) -> None:
    logger = setup_logger(
        PACKAGE_NAME,
        log_level="debug" if verbose else log_level,
        infect=not DISABLE_RICH,
    )
    if DISABLE_RICH:
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
    for source in track(app.sources, description="Importing", disable=DISABLE_RICH):
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
    console.print(f"Imported '{item.title}' from {item.uri}")


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


def find_item(app: Application, source_id: str, uid: str) -> SourceItem:
    items = app.get_items(ProcessingScope(source=source_id, uids=(uid,)))
    if not items:
        raise click.ClickException(f"item '{source_id}/{uid}' not found")
    return items[0]


@cli.command("items")
@scope_options
@click.pass_context
@report_user_errors
def items_cmd(ctx: click.Context, scope: ProcessingScope) -> None:
    """List stored items, oldest first."""
    items = app_from_context(ctx).get_items(scope)
    print_table(
        "Items",
        ["Source", "UID", "Published", "Title"],
        [
            [
                item.source.id,
                item.uid,
                f"{item.published_at:%Y-%m-%d %H:%M}",
                item.title,
            ]
            for item in items
        ],
    )


@cli.command("annotations")
@click.option("--source", "source_id", required=True, help="Source id")
@click.option("--uid", required=True, help="Item uid within the source")
@click.option("--processor", default=None, help="Only this processor's annotations")
@click.option("--key", default=None, help="Only this key, printed in full")
@click.pass_context
@report_user_errors
def annotations_cmd(
    ctx: click.Context,
    source_id: str,
    uid: str,
    processor: str | None,
    key: str | None,
) -> None:
    """Show an item's annotations: a preview table, or full values with --key."""
    app = app_from_context(ctx)
    item = find_item(app, source_id, uid)
    annotations = app.get_annotations(item, processor=processor, key=key)
    if not annotations:
        console.print(f"No annotations for '{source_id}/{uid}'")
        return

    rows = [
        (name, annotation_key, value)
        for name, values in annotations.items()
        for annotation_key, value in values.items()
    ]
    if key is None:
        print_table(
            f"Annotations of {source_id}/{uid}",
            ["Processor", "Key", "Value"],
            [
                [name, annotation_key, preview(value)]
                for name, annotation_key, value in rows
            ],
        )
        return

    for name, annotation_key, value in rows:
        if len(rows) > 1:
            click.echo(f"== {name}.{annotation_key}")
        click.echo(format_value(value))


@cli.command("artifacts")
@click.option("--remixer", default=None, help="Only this remixer's artifacts")
@click.pass_context
@report_user_errors
def artifacts_cmd(ctx: click.Context, remixer: str | None) -> None:
    """List stored artifacts."""
    artifacts = app_from_context(ctx).list_artifacts(remixer)
    print_table(
        "Artifacts",
        ["Remixer", "Name", "Type", "Updated"],
        [
            [a.remixer, a.name, a.content_type, f"{a.updated_at:%Y-%m-%d %H:%M}"]
            for a in artifacts
        ],
    )


@cli.command("artifact")
@click.argument("remixer")
@click.argument("name")
@click.pass_context
@report_user_errors
def artifact_cmd(ctx: click.Context, remixer: str, name: str) -> None:
    """Print an artifact's content to stdout and its metadata to stderr."""
    artifact = app_from_context(ctx).get_artifact(remixer, name)
    if artifact is None or artifact.content is None:
        raise click.ClickException(f"artifact '{remixer}/{name}' does not exist")

    click.echo(
        f"{remixer}/{name} · {artifact.content_type} · "
        f"updated {artifact.updated_at:%Y-%m-%d %H:%M}",
        err=True,
    )
    lexer = lexer_for(artifact.content_type)
    if not DISABLE_RICH and lexer and sys.stdout.isatty():
        console.print(Syntax(artifact.content, lexer))
    else:
        sys.stdout.write(artifact.content)
