BEGIN;

CREATE TYPE status_types AS ENUM ('active', 'blocked');
ALTER TABLE "user" ADD "status" status_types NOT NULL DEFAULT 'active';

COMMIT;
