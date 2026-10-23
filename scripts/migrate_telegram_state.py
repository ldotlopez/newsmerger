#!/usr/bin/env python
"""Turn the old `telegram/state` artifact into delivery ledger rows
(decision 0007): `posted` items become `done` rows with their `message_id`,
`queue` items become `queued` rows. `watermark` and `last_post` are dropped,
and the artifact is left in place.

Run it once, before the first `deliver telegram`; without it, the summarized
items of the last `lookback` hours are posted again. Running it again does
nothing: items that already have a row keep it.

Usage:
    python scripts/migrate_telegram_state.py -c config.yaml
"""  # noqa: EXE001

from __future__ import annotations

import json
import logging
from pathlib import Path

import rich_click as click
from foundation.loglib import setup_logger

from newsmerger.app import LockedError, write_lock
from newsmerger.config import Config
from newsmerger.consts import PACKAGE_NAME
from newsmerger.db import Database, DeliveryStatus
from newsmerger.models import ItemKey, ProcessingScope, SourceItem

LOGGER = logging.getLogger(PACKAGE_NAME)

SINK = "telegram"


def migrate(db: Database) -> tuple[int, int]:
    """Record the state's posted items as done and give its queued items a
    row; return how many were recorded as done and how many are queued."""
    artifact = db.get_artifact(SINK, "state")
    if artifact is None or artifact.content is None:
        raise click.ClickException("there is no telegram/state artifact to migrate")
    state = json.loads(artifact.content)
    posted: dict[ItemKey, int] = {
        (source_id, uid): message_id for source_id, uid, message_id in state["posted"]
    }
    queued: list[ItemKey] = [(source_id, uid) for source_id, uid in state["queue"]]

    items: dict[ItemKey, SourceItem] = {}
    for source_id in {source_id for source_id, _ in [*posted, *queued]}:
        items.update(
            (item.key, item) for item in db.get_items(ProcessingScope(source=source_id))
        )
    for key in [*posted, *queued]:
        if key not in items:
            LOGGER.warning(f"item {key[0]}/{key[1]} is no longer stored; skipped")

    posted_ids = tuple(items[key].id for key in posted if key in items)
    queued_ids = tuple(items[key].id for key in queued if key in items)
    for item_ids in (posted_ids, queued_ids):
        # An empty selection would be no filter at all, and queue every item.
        if item_ids:
            db.queue_item_deliveries(SINK, ProcessingScope(item_ids=item_ids))

    done = 0
    if posted_ids:
        for delivery, item in db.get_item_deliveries(
            SINK, ProcessingScope(item_ids=posted_ids)
        ):
            if delivery.status == DeliveryStatus.DONE:
                continue  # recorded before this run
            delivery.status = DeliveryStatus.DONE
            delivery.attempts = 0
            delivery.last_error = None
            delivery.external_ref = {"message_id": posted[item.key]}
            delivery.content_sha256 = item.content_sha256
            db.save_delivery(delivery)
            done += 1
    return done, len(queued_ids)


@click.command()
@click.option("-c", "--config", "config_path", type=Path, default=None)
def main(config_path: Path | None) -> None:
    setup_logger(PACKAGE_NAME, log_level="info")
    config = Config.from_file(config_path) if config_path else Config()
    try:
        lock = write_lock(config.db.uri)
    except LockedError as e:
        raise click.ClickException(str(e)) from e
    db = Database(config.db.uri, config.db.content_dir)
    try:
        done, queued = migrate(db)
    finally:
        db.close()
        if lock is not None:
            lock.close()
    click.echo(f"Recorded {done} posted item(s) as done and queued {queued}")


if __name__ == "__main__":
    main()
