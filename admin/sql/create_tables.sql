BEGIN;

CREATE TABLE license (
  id        VARCHAR    NOT NULL,
  full_name VARCHAR    NOT NULL,
  info_url  VARCHAR
);

CREATE TABLE moderation_log (
    id          SERIAL       NOT NULL,
    admin_id    UUID         NOT NULL,
    user_id     UUID,
    review_id   UUID,
    action      action_types NOT NULL,
    "timestamp" TIMESTAMP    NOT NULL,
    reason      VARCHAR      NOT NULL
);

CREATE TABLE oauth_client (
    client_id     VARCHAR NOT NULL,
    client_secret VARCHAR NOT NULL,
    redirect_uri  TEXT    NOT NULL,
    user_id       UUID,
    name          VARCHAR NOT NULL,
    "desc"        VARCHAR NOT NULL,
    website       VARCHAR NOT NULL
);

CREATE TABLE oauth_grant (
    id           SERIAL      NOT NULL,
    client_id    VARCHAR     NOT NULL,
    code         VARCHAR     NOT NULL,
    expires      TIMESTAMP   NOT NULL,
    redirect_uri TEXT        NOT NULL,
    scopes       TEXT,
    user_id      UUID        NOT NULL
);

CREATE TABLE oauth_token (
    id            SERIAL      NOT NULL,
    client_id     VARCHAR     NOT NULL,
    access_token  VARCHAR     NOT NULL,
    refresh_token VARCHAR     NOT NULL,
    expires       TIMESTAMP   NOT NULL,
    scopes        TEXT,
    user_id       UUID        NOT NULL
);
ALTER TABLE oauth_token ADD CONSTRAINT oauth_token_access_token_key UNIQUE (access_token);
ALTER TABLE oauth_token ADD CONSTRAINT oauth_token_refresh_token_key UNIQUE (refresh_token);

CREATE TABLE review (
    id          UUID         NOT NULL DEFAULT uuid_generate_v4(),
    entity_id   UUID         NOT NULL,
    entity_type entity_types NOT NULL,
    user_id     UUID         NOT NULL,
    edits       INTEGER      NOT NULL,
    is_draft    BOOLEAN      NOT NULL,
    is_hidden   BOOLEAN      NOT NULL,
    license_id  VARCHAR      NOT NULL,
    language    VARCHAR(3)   NOT NULL,
    source      VARCHAR,
    source_url  VARCHAR
);
ALTER TABLE review ADD CONSTRAINT review_entity_id_user_id_key UNIQUE (entity_id, user_id);

CREATE TABLE revision (
    id          SERIAL      NOT NULL,
    review_id   UUID,
    "timestamp" TIMESTAMP   NOT NULL,
    text        VARCHAR,     
    rating      SMALLINT CHECK (rating >= 0 AND rating <= 100)
);
ALTER TABLE revision ADD CONSTRAINT revision_text_rating_both_not_null_together
    CHECK (rating is NOT NULL OR text is NOT NULL);

CREATE TABLE avg_rating (
    entity_id   UUID         NOT NULL,
    entity_type entity_types NOT NULL,
    rating      SMALLINT     NOT NULL CHECK (rating >= 0 AND rating <= 100),
    count       INTEGER      NOT NULL
);

CREATE TABLE spam_report (
    user_id     UUID        NOT NULL,
    reason      VARCHAR,
    revision_id INTEGER     NOT NULL,
    reported_at TIMESTAMP   NOT NULL,
    is_archived BOOLEAN     NOT NULL
);

CREATE TABLE "user" (
    id             UUID        NOT NULL DEFAULT uuid_generate_v4(),
    display_name   VARCHAR     NOT NULL,
    email          VARCHAR,
    created        TIMESTAMP   NOT NULL,
    musicbrainz_id VARCHAR,
    show_gravatar  BOOLEAN     NOT NULL DEFAULT False,
    is_blocked     BOOLEAN     NOT NULL DEFAULT False
);
ALTER TABLE "user" ADD CONSTRAINT user_musicbrainz_id_key UNIQUE (musicbrainz_id);

CREATE TABLE vote (
    user_id     UUID        NOT NULL,
    revision_id INTEGER     NOT NULL,
    vote        BOOLEAN     NOT NULL,
    rated_at    TIMESTAMP   NOT NULL
);

COMMIT;
