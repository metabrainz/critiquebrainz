BEGIN;
CREATE INDEX ix_user_id ON "user" USING btree ((id::text));
COMMIT;
