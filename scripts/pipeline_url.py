#!/usr/bin/env python
"""Import one article URL into a configured source, then run processors on it
in the given order, stopping at the first one that produces no output.

Pipelines live outside the core while the feature is in development
(decision 0003); this is the publish-news flow on top of Application.

Usage:
    python scripts/pipeline_url.py -c config.yaml --source castellonplaza \\
        https://castellonplaza.com/... markdownify summarize tagger
"""  # noqa: EXE001

from __future__ import annotations

from pathlib import Path

import rich_click as click
from foundation.loglib import setup_logger

from newsmerger.app import Application
from newsmerger.consts import PACKAGE_NAME
from newsmerger.models import ProcessingScope


@click.command()
@click.option("-c", "--config", "config_path", type=Path, default=None)
@click.option("--source", "source_id", required=True, help="Configured source id")
@click.option("--force", is_flag=True, help="Re-run processors that already finished")
@click.argument("url")
@click.argument("processors", nargs=-1, required=True)
def main(
    config_path: Path | None,
    source_id: str,
    force: bool,
    url: str,
    processors: tuple[str, ...],
) -> None:
    setup_logger(PACKAGE_NAME, log_level="info")

    with Application.from_config_file(config_path) as app:
        item = app.import_url(source_id, url)
        scope = ProcessingScope(source=item.source.id, uids=(item.uid,))
        for processor in processors:
            app.run_processor(processor, scope=scope, force=force)
            if not app.get_annotations(item, processor=processor):
                raise click.ClickException(
                    f"processor '{processor}' produced no output for {url}"
                )

    click.echo(f"Processed '{item.title}' with {', '.join(processors)}")


if __name__ == "__main__":
    main()
