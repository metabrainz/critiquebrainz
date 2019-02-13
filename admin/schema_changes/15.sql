BEGIN;

ALTER TYPE action_types ADD VALUE 'unhide_review' AFTER 'hide_review';
ALTER TYPE action_types ADD VALUE 'unblock_user' AFTER 'block_user';

COMMIT;
