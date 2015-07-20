BEGIN;

CREATE TYPE action_types AS ENUM (
    'archive_review',
    'ban_user'
);

CREATE TABLE admin_log (
    id integer NOT NULL,
    admin_id uuid,
    user_id uuid,
    action action_types,
    "timestamp" timestamp without time zone NOT NULL
);

COMMIT;
