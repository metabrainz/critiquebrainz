BEGIN;

CREATE TYPE user_status_types AS ENUM (
    'active',
    'blocked'
);

ALTER TABLE "user" ADD "status" user_status_types NOT NULL DEFAULT 'active';

CREATE TYPE action_types AS ENUM (
    'archive_review',
    'block_user'
);

CREATE TABLE moderation_log (
    id SERIAL NOT NULL,
    admin_id UUID NOT NULL,
    user_id UUID,
    review_id UUID,
    action action_types NOT NULL,
    timestamp TIMESTAMP WITHOUT TIME ZONE NOT NULL,
    reason VARCHAR NOT NULL,
    PRIMARY KEY (id),
    FOREIGN KEY(admin_id) REFERENCES "user" (id) ON DELETE CASCADE,
    FOREIGN KEY(user_id) REFERENCES "user" (id) ON DELETE CASCADE,
    FOREIGN KEY(review_id) REFERENCES review (id) ON DELETE CASCADE
);

ALTER TABLE spam_report ADD COLUMN is_archive boolean NOT NULL DEFAULT FALSE;
ALTER TABLE review ADD COLUMN is_archive boolean NOT NULL DEFAULT FALSE;

COMMIT;
