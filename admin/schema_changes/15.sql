-- NOTE: this cannot be inside a transaction because
-- postgres currently does not support adding values
-- to enums inside a transaction block
ALTER TYPE action_types ADD VALUE 'unhide_review' AFTER 'hide_review';
ALTER TYPE action_types ADD VALUE 'unblock_user' AFTER 'block_user';
