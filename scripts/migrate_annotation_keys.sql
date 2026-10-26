-- Key processing state and annotations by (item, key) (decision 0002):
-- processing_state gets a `key` column, and both tables become unique per
-- (source_item_id, key). Every row and id is kept, and so is each table's
-- AUTOINCREMENT counter, so deleted ids are never reused (decision 0008).
--
-- A state's key is the annotation key its processor wrote. `embed`, which
-- wrote several keys per run, gets one state per embedding it stored; its
-- `tags_text` annotations are dropped (their content files are left
-- orphaned on disk). Unknown processors keep their name as the key.
--
-- Back up the database first, with no newsmerger command running. Run once:
--     sqlite3 -bail data.db < scripts/migrate_annotation_keys.sql

PRAGMA foreign_keys = OFF;
BEGIN;

CREATE TEMP TABLE saved_sequence AS
    SELECT name, seq FROM sqlite_sequence
    WHERE name IN ('processing_state', 'item_annotations');

-- processing_state ----------------------------------------------------------

CREATE TABLE processing_state__new (
	id INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT,
	source_item_id INTEGER NOT NULL,
	processor VARCHAR(255) NOT NULL,
	"key" VARCHAR(255) NOT NULL,
	status VARCHAR(50) NOT NULL,
	attempts INTEGER NOT NULL,
	last_error TEXT,
	processor_version VARCHAR(255),
	content_sha256 VARCHAR(64) NOT NULL,
	created_at DATETIME NOT NULL,
	updated_at DATETIME NOT NULL,
	UNIQUE (source_item_id, "key"),
	CONSTRAINT ck_processing_state_status CHECK (status IN ('done', 'error', 'ignored')),
	FOREIGN KEY(source_item_id) REFERENCES source_items (id) ON DELETE CASCADE
);

INSERT INTO processing_state__new (
    id, source_item_id, processor, "key", status, attempts, last_error,
    processor_version, content_sha256, created_at, updated_at
)
SELECT
    id, source_item_id, processor,
    CASE processor
        WHEN 'markdownify' THEN 'markdown'
        WHEN 'summarize' THEN 'summary'
        WHEN 'tagger' THEN 'tags'
        WHEN 'telegram' THEN 'message_id'
        ELSE processor
    END,
    status, attempts, last_error, processor_version, content_sha256,
    created_at, updated_at
FROM processing_state
WHERE processor <> 'embed';

-- embed states without an embedding (errors, skips) count as the default run.
INSERT INTO processing_state__new (
    id, source_item_id, processor, "key", status, attempts, last_error,
    processor_version, content_sha256, created_at, updated_at
)
SELECT
    id, source_item_id, processor, 'tags_embedding', status, attempts,
    last_error, processor_version, content_sha256, created_at, updated_at
FROM processing_state AS s
WHERE s.processor = 'embed'
    AND NOT EXISTS (
        SELECT 1 FROM item_annotations AS a
        WHERE a.source_item_id = s.source_item_id
            AND a.processor = 'embed'
            AND a."key" IN ('tags_embedding', 'markdown_embedding')
    );

-- One state per embedding embed stored for the item, with new ids (after
-- every row that keeps its id, so none collides).
INSERT INTO processing_state__new (
    source_item_id, processor, "key", status, attempts, last_error,
    processor_version, content_sha256, created_at, updated_at
)
SELECT
    s.source_item_id, s.processor, a."key", s.status, s.attempts,
    s.last_error, s.processor_version, s.content_sha256, s.created_at,
    s.updated_at
FROM processing_state AS s
JOIN item_annotations AS a
    ON a.source_item_id = s.source_item_id
    AND a.processor = 'embed'
    AND a."key" IN ('tags_embedding', 'markdown_embedding')
WHERE s.processor = 'embed';

DROP TABLE processing_state;
ALTER TABLE processing_state__new RENAME TO processing_state;
CREATE INDEX ix_processing_state_processor_status ON processing_state (processor, status);

-- item_annotations ----------------------------------------------------------

CREATE TABLE item_annotations__new (
	id INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT,
	source_item_id INTEGER NOT NULL,
	processor VARCHAR(255) NOT NULL,
	"key" VARCHAR(255) NOT NULL,
	content_sha256 VARCHAR(64) NOT NULL,
	created_at DATETIME NOT NULL,
	updated_at DATETIME NOT NULL,
	UNIQUE (source_item_id, "key"),
	FOREIGN KEY(source_item_id) REFERENCES source_items (id) ON DELETE CASCADE
);

INSERT INTO item_annotations__new (
    id, source_item_id, processor, "key", content_sha256, created_at,
    updated_at
)
SELECT
    id, source_item_id, processor, "key", content_sha256, created_at,
    updated_at
FROM item_annotations
WHERE NOT (processor = 'embed' AND "key" = 'tags_text');

DROP TABLE item_annotations;
ALTER TABLE item_annotations__new RENAME TO item_annotations;
CREATE INDEX ix_item_annotations_processor ON item_annotations (processor);
CREATE INDEX ix_item_annotations_content_sha256 ON item_annotations (content_sha256);

-- Counters ------------------------------------------------------------------

UPDATE sqlite_sequence
SET seq = max(
    seq, (SELECT saved.seq FROM saved_sequence AS saved
          WHERE saved.name = sqlite_sequence.name)
)
WHERE name IN (SELECT name FROM saved_sequence);

DROP TABLE saved_sequence;

COMMIT;
PRAGMA foreign_keys = ON;
PRAGMA foreign_key_check;
