BEGIN;

-- there was a bug in the schema change that added the published_on column
-- the query was incorrect and the constraint wasn't added, leading to bad
-- data dumps. This should fix it.
UPDATE review ro
   SET published_on = (SELECT MAX(rv.timestamp) FROM review r JOIN revision rv ON r.id = rv.review_id WHERE r.id = ro.id)
 WHERE is_draft = 'f' AND published_on IS NULL;

ALTER TABLE review ADD CONSTRAINT published_on_null_for_drafts_and_not_null_for_published_reviews
    CHECK ((is_draft = 't' AND published_on IS NULL) OR (is_draft = 'f' AND published_on IS NOT NULL));

COMMIT;
