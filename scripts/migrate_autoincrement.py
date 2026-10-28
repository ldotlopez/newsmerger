#!/usr/bin/env python
"""Recreate the tables of an existing database with AUTOINCREMENT ids
(decision 0008), keeping every row and id. Runs once; tables that already
have it are left alone, so running it again does nothing.

Back the database up first. It takes the write lock, so it fails at once
if another newstool command is using the database.

Usage:
    python scripts/migrate_autoincrement.py -c config.yaml
"""  # noqa: EXE001

from __future__ import annotations

import sqlite3
from pathlib import Path

import rich_click as click
from sqlalchemy import MetaData, Table, make_url
from sqlalchemy.dialects import sqlite
from sqlalchemy.schema import CreateIndex, CreateTable

from newstool.app import LockedError, write_lock
from newstool.config import Config
from newstool.db import Base


def needs_autoincrement(connection: sqlite3.Connection, table: Table) -> bool:
    if not table.dialect_options["sqlite"]["autoincrement"]:
        return False
    row = connection.execute(
        "SELECT sql FROM sqlite_master WHERE type = 'table' AND name = ?",
        (table.name,),
    ).fetchone()
    return row is not None and "AUTOINCREMENT" not in row[0].upper()


def recreate(connection: sqlite3.Connection, table: Table, metadata: MetaData) -> None:
    """Copy `table` into a new one declared as the model says, then swap them.

    Follows SQLite's procedure for schema changes: create, copy, drop, rename.
    """
    dialect = sqlite.dialect()
    staging = table.to_metadata(metadata, name=f"{table.name}__new")
    indexes = connection.execute(
        "SELECT name FROM sqlite_master"
        " WHERE type = 'index' AND tbl_name = ? AND sql IS NOT NULL",
        (table.name,),
    ).fetchall()
    for (index,) in indexes:
        connection.execute(f'DROP INDEX "{index}"')

    connection.execute(str(CreateTable(staging).compile(dialect=dialect)))
    columns = ", ".join(f'"{column.name}"' for column in table.columns)
    connection.execute(
        f'INSERT INTO "{staging.name}" ({columns}) SELECT {columns} FROM "{table.name}"'
    )
    connection.execute(f'DROP TABLE "{table.name}"')
    connection.execute(f'ALTER TABLE "{staging.name}" RENAME TO "{table.name}"')
    for index in table.indexes:
        connection.execute(str(CreateIndex(index).compile(dialect=dialect)))


def migrate(db_path: Path) -> list[str]:
    """Migrate the tables that lack AUTOINCREMENT, in one transaction;
    return their names."""
    # A copy of the models' metadata, where the staging tables can resolve
    # their foreign keys.
    metadata = MetaData()
    for table in Base.metadata.sorted_tables:
        table.to_metadata(metadata)

    connection = sqlite3.connect(db_path, isolation_level=None)
    try:
        # Off while tables are swapped; it cannot change inside a transaction.
        connection.execute("PRAGMA foreign_keys = OFF")
        connection.execute("BEGIN")
        try:
            migrated = []
            for table in metadata.sorted_tables:
                if needs_autoincrement(connection, table):
                    recreate(connection, table, metadata)
                    migrated.append(table.name)
            if broken := connection.execute("PRAGMA foreign_key_check").fetchall():
                raise RuntimeError(f"foreign keys broken by the migration: {broken}")
            connection.execute("COMMIT")
        except BaseException:
            connection.execute("ROLLBACK")
            raise
    finally:
        connection.close()
    return migrated


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
        migrated = migrate(db_path)
    finally:
        if lock is not None:
            lock.close()
    click.echo(f"Migrated {', '.join(migrated)}" if migrated else "Nothing to migrate")


if __name__ == "__main__":
    main()
