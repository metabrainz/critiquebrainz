ALTER TYPE entity_types ADD VALUE 'bb_literary_work' AFTER 'bb_edition_group';
ALTER TYPE entity_types ADD VALUE 'bb_author' AFTER 'bb_literary_work';
ALTER TYPE entity_types ADD VALUE 'bb_series' AFTER 'bb_author';
