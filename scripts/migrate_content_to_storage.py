"""One-shot migration: move source_items.content into the content storage.

Run it once, before the first run of the storage-backed code. It backs up
the database, adds the mimetype/content_sha256 columns, writes every row's
content to the DiskStorage at config.db.content_dir and drops the content
column. Safe to re-run after a failure: migrated rows are skipped and an
existing backup is never overwritten.

shortcut: SQLite's ALTER TABLE cannot add NOT NULL or CHECK constraints, so a
migrated table lacks the ones a fresh schema has; rebuild it if they matter.
"""

import argparse
import hashlib
import shutil
import sqlite3
from pathlib import Path

from foundation.storage import DiskStorage

from newsmerger.config import Config

SQLITE_PREFIX = "sqlite:///"


def sqlite_path(database_url: str) -> Path:
    if not database_url.startswith(SQLITE_PREFIX):
        raise ValueError(f"only file SQLite databases are supported: {database_url}")
    return Path(database_url.removeprefix(SQLITE_PREFIX))


def column_names(conn: sqlite3.Connection) -> set[str]:
    return {row[1] for row in conn.execute("PRAGMA table_info(source_items)")}


def migrate(db_path: Path, contents: DiskStorage) -> int:
    """Migrate the database at db_path and return how many rows were moved."""
    conn = sqlite3.connect(db_path)
    try:
        columns = column_names(conn)
        if "content" not in columns:
            return 0
        if "mimetype" not in columns:
            conn.execute("ALTER TABLE source_items ADD COLUMN mimetype VARCHAR(255)")
        if "content_sha256" not in columns:
            conn.execute(
                "ALTER TABLE source_items ADD COLUMN content_sha256 VARCHAR(64)"
            )
        conn.execute(
            "CREATE INDEX IF NOT EXISTS ix_source_items_content_sha256 "
            "ON source_items (content_sha256)"
        )

        rows = conn.execute(
            "SELECT id, content FROM source_items WHERE content_sha256 IS NULL"
        ).fetchall()
        for item_id, text in rows:
            content = text.encode("utf-8")
            sha256 = hashlib.sha256(content).hexdigest()
            # Content first, row second: a crash leaves an unused file, not a
            # row pointing at nothing.
            contents.set(sha256, content)
            conn.execute(
                "UPDATE source_items SET mimetype = 'text/html', content_sha256 = ? "
                "WHERE id = ?",
                (sha256, item_id),
            )
        conn.commit()

        conn.execute("ALTER TABLE source_items DROP COLUMN content")
        conn.commit()
        return len(rows)
    finally:
        conn.close()


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument(
        "--config",
        type=Path,
        help="Path to config.yaml (defaults to Config() built-in defaults)",
    )
    args = parser.parse_args()

    config = Config.from_file(args.config) if args.config else Config()
    db_path = sqlite_path(config.db.uri)
    backup_path = db_path.with_name(db_path.name + ".bak")
    if not backup_path.exists():
        shutil.copy2(db_path, backup_path)

    contents = DiskStorage(config.db.content_dir)
    try:
        migrated = migrate(db_path, contents)
    finally:
        contents.close()
    print(f"Migrated {migrated} items. Backup: {backup_path}")


if __name__ == "__main__":
    main()
