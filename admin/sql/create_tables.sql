BEGIN;

CREATE TABLE comment (
    id          UUID        NOT NULL DEFAULT uuid_generate_v4(),
    review_id   UUID        NOT NULL,
    user_id     UUID        NOT NULL,
    edits       INTEGER     NOT NULL DEFAULT 0,
    is_draft    BOOLEAN     NOT NULL DEFAULT False,
    is_hidden   BOOLEAN     NOT NULL DEFAULT False
);

CREATE TABLE comment_revision (
    id          SERIAL      NOT NULL,
    comment_id  UUID        NOT NULL,
    "timestamp" TIMESTAMP   NOT NULL DEFAULT NOW(),
    text        VARCHAR     NOT NULL CHECK (text <> '')
);

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
    id              UUID         NOT NULL DEFAULT uuid_generate_v4(),
    entity_id       UUID         NOT NULL,
    entity_type     entity_types NOT NULL,
    user_id         UUID         NOT NULL,
    edits           INTEGER      NOT NULL,
    is_draft        BOOLEAN      NOT NULL,
    is_hidden       BOOLEAN      NOT NULL,
    license_id      VARCHAR,
    language        VARCHAR(3)   NOT NULL,
    published_on    TIMESTAMP,
    source          VARCHAR,
    source_url      VARCHAR
);
ALTER TABLE review ADD CONSTRAINT review_entity_id_user_id_key UNIQUE (entity_id, user_id);
ALTER TABLE review ADD CONSTRAINT published_on_null_for_drafts_and_not_null_for_published_reviews
    CHECK ((is_draft = 't' AND published_on IS NULL) OR (is_draft = 'f' And published_on IS NOT NULL));
ALTER TABLE review ADD CONSTRAINT license_id_not_null_is_draft_false
    CHECK ((is_draft = 'f' AND license_id IS NOT NULL) OR is_draft = 't');

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
    id                  UUID        NOT NULL DEFAULT uuid_generate_v4(),
    display_name        VARCHAR     NOT NULL,
    email               VARCHAR,
    created             TIMESTAMP   NOT NULL,
    musicbrainz_id      VARCHAR,
    musicbrainz_row_id  INTEGER,
    is_blocked          BOOLEAN     NOT NULL DEFAULT False,
    license_choice      VARCHAR
);
ALTER TABLE "user" ADD CONSTRAINT user_musicbrainz_id_key UNIQUE (musicbrainz_id);
ALTER TABLE "user" ADD CONSTRAINT user_musicbrainz_row_id_key UNIQUE (musicbrainz_row_id);

CREATE TABLE vote (
    user_id     UUID        NOT NULL,
    revision_id INTEGER     NOT NULL,
    vote        BOOLEAN     NOT NULL,
    rated_at    TIMESTAMP   NOT NULL
);

COMMIT;
