BEGIN;

ALTER TABLE review ADD CONSTRAINT license_id_not_null_is_draft_false
    CHECK ((is_draft = 'f' AND license_id IS NOT NULL) OR is_draft = 't');

ALTER TABLE review ALTER COLUMN license_id DROP NOT NULL;

-- to change the ON DELETE action of foreign key need to drop and recreate it
ALTER TABLE review DROP CONSTRAINT review_license_id_fkey;

ALTER TABLE review
  ADD CONSTRAINT review_license_id_fkey
  FOREIGN KEY (license_id)
  REFERENCES license(id)
  ON DELETE SET NULL;

COMMIT;
