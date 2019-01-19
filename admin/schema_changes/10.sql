BEGIN;

ALTER TABLE "user" ADD COLUMN license_choice VARCHAR;

ALTER TABLE "user"
  ADD CONSTRAINT user_license_choice_fkey
  FOREIGN KEY (license_choice)
  REFERENCES license(id)
  ON DELETE CASCADE;

COMMIT;
