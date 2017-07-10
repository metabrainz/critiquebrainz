BEGIN;

ALTER TABLE revision ALTER COLUMN text DROP NOT NULL; 
ALTER TABLE revision ADD COLUMN rating SMALLINT;

ALTER TABLE revision ADD CONSTRAINT revision_rating_check CHECK (rating >= 0 AND rating <=100);
ALTER TABLE revision ADD CONSTRAINT revision_text_rating_both_not_null_together
    CHECK (rating is NOT NULL OR text is NOT NULL);

CREATE TABLE avg_rating (
    entity_id   UUID         NOT NULL,
    entity_type entity_types NOT NULL,
    rating      SMALLINT     NOT NULL CHECK (rating >= 0 AND rating <= 100),
    count       INTEGER      NOT NULL,
    PRIMARY KEY (entity_id, entity_type)
);

COMMIT;
