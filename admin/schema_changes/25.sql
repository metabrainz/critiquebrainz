BEGIN;

ALTER TABLE comment
    ALTER COLUMN id SET DEFAULT gen_random_uuid();

ALTER TABLE review
    ALTER COLUMN id SET DEFAULT gen_random_uuid();

ALTER TABLE "user"
    ALTER COLUMN id SET DEFAULT gen_random_uuid();

DROP EXTENSION IF EXISTS "uuid-ossp";

COMMIT;
