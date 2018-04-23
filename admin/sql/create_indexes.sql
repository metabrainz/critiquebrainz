BEGIN;

CREATE UNIQUE INDEX review_entity_id_user_id_index ON review (entity_id, user_id) WHERE (blurb = 'f');
CREATE INDEX ix_oauth_grant_code ON oauth_grant USING btree (code);
CREATE INDEX ix_review_entity_id ON review USING btree (entity_id);
CREATE INDEX ix_revision_review_id ON revision USING btree (review_id);

COMMIT;
