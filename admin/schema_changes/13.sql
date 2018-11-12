BEGIN;

ALTER TABLE "comment_revision"
  ALTER COLUMN text
  SET NOT NULL,
  ADD CHECK (text <> '');

COMMIT;