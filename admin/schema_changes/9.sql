BEGIN;

CREATE TABLE follower (
    follower_id     UUID,
    following_id    UUID
);


ALTER TABLE follower ADD CONSTRAINT follower_pkey PRIMARY KEY (follower_id, following_id);


ALTER TABLE follower
  ADD CONSTRAINT follower_follower_id_fkey
  FOREIGN KEY (following_id)
  REFERENCES "user"(id)
  ON DELETE CASCADE;

ALTER TABLE follower
  ADD CONSTRAINT follower_following_id_fkey
  FOREIGN KEY (follower_id)
  REFERENCES "user"(id)
  ON DELETE CASCADE;

COMMIT;
