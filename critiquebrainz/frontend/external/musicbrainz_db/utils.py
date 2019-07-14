import critiquebrainz.frontend.external.musicbrainz_db.exceptions as mb_exceptions
from critiquebrainz.frontend.external.musicbrainz_db import special_entities
from critiquebrainz.db.review import reviewed_entities, ENTITY_TYPES as CB_ENTITIES


def unknown_entity(entity_gid, entity_type):
    """Returns special unknown entities (in case, they are not present in MB).

    Args:
        entity_gid: MBID of the unknown entity.
        entity_type: Type of the unknown entity.
    Returns:
        Special entity object (unknown) of specified entity_type.
    """
    if entity_type == 'release_group':
        entity = special_entities.unknown_release_group
    elif entity_type == 'place':
        entity = special_entities.unknown_place
    elif entity_type == 'event':
        entity = special_entities.unknown_event
    entity.gid = entity_gid
    return entity


def deleted_entities_to_unknown(*, entities, entity_type, mbids):
    """Set deleted entities with reviews as unknown.

    Args:
        entities (dict): Dictionary of objects containing entities.
        entity_type (str): Type of entity being queried.
        mbids (list): IDs of the entities.

    Returns:
        Dictionary of objects with missing, but reviewed, mbids set as unknown.
    """
    if mbids and entity_type in CB_ENTITIES:
        reviewed_gids = reviewed_entities(
            entity_ids=mbids,
            entity_type=entity_type,
        )
        for gid in reviewed_gids:
            if gid not in entities:
                entities[gid] = unknown_entity(gid, entity_type)
        mbids = list(set(mbids) - set(reviewed_gids))

    if mbids:
        raise mb_exceptions.NoDataFoundException("Couldn't find entities with IDs: {mbids}".format(mbids=mbids))
    return entities
