BEGIN;

CREATE INDEX ix_oauth_grant_code ON oauth_grant (code);
CREATE INDEX ix_review_entity_id ON review (entity_id);
CREATE INDEX ix_revision_review_id ON revision (review_id);

COMMIT;
