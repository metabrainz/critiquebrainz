BEGIN;

ALTER TABLE review
  ADD CONSTRAINT review_license_id_fkey
  FOREIGN KEY (license_id)
  REFERENCES license(id)
  ON DELETE CASCADE;

ALTER TABLE moderation_log
  ADD CONSTRAINT moderation_log_admin_id_fkey
  FOREIGN KEY (admin_id)
  REFERENCES "user"(id)
  ON DELETE CASCADE;

ALTER TABLE moderation_log
  ADD CONSTRAINT moderation_log_review_id_fkey
  FOREIGN KEY (review_id)
  REFERENCES review(id)
  ON DELETE CASCADE;

ALTER TABLE moderation_log
  ADD CONSTRAINT moderation_log_user_id_fkey
  FOREIGN KEY (user_id)
  REFERENCES "user"(id)
  ON DELETE CASCADE;

ALTER TABLE oauth_client
  ADD CONSTRAINT oauth_client_user_id_fkey
  FOREIGN KEY (user_id)
  REFERENCES "user"(id)
  ON DELETE CASCADE;

ALTER TABLE oauth_grant
  ADD CONSTRAINT oauth_grant_client_id_fkey
  FOREIGN KEY (client_id)
  REFERENCES oauth_client(client_id)
  ON UPDATE CASCADE
  ON DELETE CASCADE;

ALTER TABLE oauth_token
  ADD CONSTRAINT oauth_token_client_id_fkey
  FOREIGN KEY (client_id)
  REFERENCES oauth_client(client_id)
  ON UPDATE CASCADE
  ON DELETE CASCADE;

ALTER TABLE oauth_grant
  ADD CONSTRAINT oauth_grant_user_id_fkey
  FOREIGN KEY (user_id)
  REFERENCES "user"(id)
  ON DELETE CASCADE;

ALTER TABLE oauth_token
  ADD CONSTRAINT oauth_token_user_id_fkey
  FOREIGN KEY (user_id)
  REFERENCES "user"(id)
  ON DELETE CASCADE;

ALTER TABLE review
  ADD CONSTRAINT review_user_id_fkey
  FOREIGN KEY (user_id)
  REFERENCES "user"(id)
  ON DELETE CASCADE;

ALTER TABLE spam_report
  ADD CONSTRAINT spam_report_revision_id_fkey
  FOREIGN KEY (revision_id)
  REFERENCES revision(id)
  ON DELETE CASCADE;

ALTER TABLE vote
  ADD CONSTRAINT vote_revision_id_fkey
  FOREIGN KEY (revision_id)
  REFERENCES revision(id)
  ON DELETE CASCADE;

ALTER TABLE spam_report
  ADD CONSTRAINT spam_report_user_id_fkey
  FOREIGN KEY (user_id)
  REFERENCES "user"(id)
  ON DELETE CASCADE;

ALTER TABLE vote
  ADD CONSTRAINT vote_user_id_fkey
  FOREIGN KEY (user_id)
  REFERENCES "user"(id)
  ON DELETE CASCADE;

ALTER TABLE revision
  ADD CONSTRAINT revision_review_id_fkey
  FOREIGN KEY (review_id)
  REFERENCES review(id)
  ON DELETE CASCADE;

COMMIT;
