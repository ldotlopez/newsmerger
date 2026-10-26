#!/usr/bin/env python
"""Rename the `rssfeed` remixer's artifacts to `feedgenerator`, its new name,
keeping their ids so their deliveries stay attached. Running it again does
nothing. Sources need nothing: their `provider` (`rssparser`, now
`feedreader`) is synced from the configuration.

Rename the plugin sections and the sources' `provider:` in config.yaml
before or after; run it before the first `remix feedgenerator`, which would
otherwise build a new artifact and deliver it again.

Usage:
    python scripts/migrate_feed_names.py -c config.yaml
"""  # noqa: EXE001

from __future__ import annotations

import sqlite3
from pathlib import Path

import rich_click as click
from sqlalchemy import make_url

from newsmerger.app import LockedError, write_lock
from newsmerger.config import Config

OLD_NAME = "rssfeed"
NEW_NAME = "feedgenerator"


def migrate(db_path: Path) -> int:
    """Rename the old remixer's artifacts; return how many were renamed."""
    connection = sqlite3.connect(db_path)
    try:
        with connection:
            cursor = connection.execute(
                "UPDATE artifacts SET remixer = ? WHERE remixer = ?",
                (NEW_NAME, OLD_NAME),
            )
        return cursor.rowcount
    except sqlite3.IntegrityError as e:
        raise click.ClickException(
            f"'{NEW_NAME}' already has artifacts with the same names; delete them"
            f" (delete artifacts --remixer {NEW_NAME}) and run this again"
        ) from e
    finally:
        connection.close()


@click.command()
@click.option("-c", "--config", "config_path", type=Path, default=None)
def main(config_path: Path | None) -> None:
    config = Config.from_file(config_path) if config_path else Config()
    url = make_url(config.db.uri)
    if url.get_backend_name() != "sqlite" or not url.database:
        raise click.ClickException(f"not a SQLite database file: {config.db.uri}")
    db_path = Path(url.database)
    if not db_path.exists():
        raise click.ClickException(f"database not found: {db_path}")

    try:
        lock = write_lock(config.db.uri)
    except LockedError as e:
        raise click.ClickException(str(e)) from e
    try:
        renamed = migrate(db_path)
    finally:
        lock.close()
    click.echo(f"Renamed {renamed} artifact(s)" if renamed else "Nothing to migrate")


if __name__ == "__main__":
    main()
