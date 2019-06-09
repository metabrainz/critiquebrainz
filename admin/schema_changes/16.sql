ALTER TYPE entity_types ADD VALUE 'work' AFTER 'place';
ALTER TYPE entity_types ADD VALUE 'artist' AFTER 'work';
ALTER TYPE entity_types ADD VALUE 'recording' AFTER 'artist';
ALTER TYPE entity_types ADD VALUE 'label' AFTER 'recording';
