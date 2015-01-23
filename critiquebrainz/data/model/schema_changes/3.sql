BEGIN;

ALTER TABLE "user" ADD COLUMN mb_refresh_token CHARACTER VARYING;
ALTER TABLE "review" ADD COLUMN rating SMALLINT;
ALTER TABLE "review" DROP COLUMN edits;  -- unused column

COMMIT;
