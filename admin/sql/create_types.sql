CREATE TYPE action_types AS ENUM (
    'hide_review',
    'unhide_review',
    'block_user',
    'unblock_user'
);

CREATE TYPE entity_types AS ENUM (
    'release_group',
    'event',
    'place',
    'work',
    'artist',
    'label',
    'recording',
    'bb_edition_group',
    'bb_author'
);
