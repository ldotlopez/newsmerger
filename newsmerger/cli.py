from __future__ import annotations

import logging
from datetime import UTC
from pathlib import Path

import rich
import rich_click as click
from foundation.loglib import setup_logger

from newsmerger.app import App, PipelineError
from newsmerger.consts import PACKAGE_NAME
from newsmerger.db import ProcessingScope
from newsmerger.models import SourceData

LOGGER = logging.getLogger(PACKAGE_NAME)


def app_from_context(ctx: click.Context) -> App:
    """Build the App for this invocation and close it when the command ends."""
    app = App.from_config_file(ctx.obj["config_path"])
    ctx.call_on_close(app.close)
    return app


@click.group()
@click.option("-c", "--config", "config_path", type=Path, default=None)
@click.pass_context
def cli(ctx, config_path: Path | None):
    # ensure that ctx.obj exists and is a dict (in case `cli()` is called
    # by means other than the `if` block below)
    setup_logger(PACKAGE_NAME)
    LOGGER.setLevel(logging.DEBUG)

    ctx.ensure_object(dict)
    ctx.obj["config_path"] = config_path


@cli.command("import")
@click.pass_context
def import_cmd(ctx):
    app = app_from_context(ctx)

    rich.print(
        f"Importing {len(app.config.sources)} sources from {ctx.obj['config_path']}"
    )
    for source_config in app.config.sources:
        items = app.import_source(source_config)
        rich.print(f"Imported {len(items)} items from '{source_config.name}'")


@cli.command("import-url")
@click.option("-p", "--provider", required=True, help="Provider module name")
@click.argument("url")
@click.pass_context
def import_url_cmd(ctx, provider: str, url: str) -> None:
    app = app_from_context(ctx)

    try:
        source = SourceData(
            name=f"{provider}:{url}",
            provider=provider,
            url=url,
        )
        item = app.import_url(source)
    except ModuleNotFoundError as exc:
        raise click.ClickException(f"provider '{provider}' not found") from exc
    except ValueError as exc:
        raise click.ClickException(str(exc)) from exc

    rich.print(f"Imported item '{item.title}' from '{item.uri}'")


@cli.command("pipeline-url")
@click.argument("pipeline_name")
@click.option("-p", "--provider", required=True, help="Provider module name")
@click.option("--force", is_flag=True, help="Re-run already completed processors")
@click.argument("url")
@click.pass_context
def pipeline_url_cmd(
    ctx: click.Context,
    pipeline_name: str,
    provider: str,
    force: bool,
    url: str,
) -> None:
    app = app_from_context(ctx)

    try:
        source = SourceData(name=f"{provider}:{url}", provider=provider, url=url)
        item = app.import_url(source)
        pipeline = app.config.get_pipeline(pipeline_name)
        app.run_pipeline(item, pipeline, force=force)
    except (ModuleNotFoundError, ValueError, PipelineError) as exc:
        raise click.ClickException(str(exc)) from exc

    rich.print(
        f"Processed '{item.title}' with pipeline '{pipeline.name}' "
        f"({', '.join(step.processor for step in pipeline.steps)})"
    )


@cli.command("process")
@click.argument("processor_name")
@click.option("--source", default=None, help="Limit to a source name or uid")
@click.option("--since", type=click.DateTime(), default=None)
@click.option("--until", type=click.DateTime(), default=None)
@click.option("--limit", type=int, default=None)
@click.option(
    "--force",
    "--reprocess",
    "force",
    is_flag=True,
    default=False,
    help="Ignore stored processing state (including ignored items) and reprocess everything in scope",
)
@click.pass_context
def process_cmd(ctx, processor_name, source, since, until, limit, force):
    app = app_from_context(ctx)

    scope = ProcessingScope(
        source=source,
        since=since.replace(tzinfo=UTC) if since else None,
        until=until.replace(tzinfo=UTC) if until else None,
        limit=limit,
    )
    app.run_processor(processor_name, scope=scope, force=force)
