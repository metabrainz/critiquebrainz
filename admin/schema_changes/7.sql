BEGIN;

ALTER TYPE entity_types ADD VALUE 'place' AFTER 'event';

COMMIT;
