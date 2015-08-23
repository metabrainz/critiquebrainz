BEGIN;

ALTER TABLE review RENAME COLUMN release_group TO entity_id;

CREATE TYPE entity_types AS enum (
    'event',
    'release_group'
);

ALTER TABLE review ADD entity_type entity_types NOT NULL DEFAULT 'release_group';
ALTER TABLE review ALTER COLUMN entity_type DROP DEFAULT;

COMMIT;
