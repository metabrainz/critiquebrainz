BEGIN;
-- allow users to comment on reviews
CREATE TABLE comment (
    id          UUID        NOT NULL DEFAULT uuid_generate_v4(),
    review_id   UUID        NOT NULL,
    user_id     UUID        NOT NULL,
    edits       INTEGER     NOT NULL DEFAULT 0,
    is_draft    BOOLEAN     NOT NULL DEFAULT False,
    is_hidden   BOOLEAN     NOT NULL DEFAULT False
);

CREATE TABLE comment_revision (
    id          SERIAL NOT NULL,
    comment_id  UUID   NOT NULL,
    "timestamp" TIMESTAMP NOT NULL DEFAULT NOW(),
    text        VARCHAR
);

ALTER TABLE comment ADD CONSTRAINT comment_pkey PRIMARY KEY (id);
ALTER TABLE comment_revision ADD CONSTRAINT comment_revision_pkey PRIMARY KEY (id);

ALTER TABLE comment
  ADD CONSTRAINT comment_review_fkey
  FOREIGN KEY (review_id)
  REFERENCES review(id)
  ON DELETE CASCADE;

ALTER TABLE comment_revision
  ADD CONSTRAINT comment_revision_comment_fkey
  FOREIGN KEY (comment_id)
  REFERENCES comment(id)
  ON DELETE CASCADE;

COMMIT;
