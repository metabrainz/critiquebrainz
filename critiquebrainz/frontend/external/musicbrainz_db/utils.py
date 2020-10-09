from mbdata import models

import critiquebrainz.frontend.external.musicbrainz_db.exceptions as mb_exceptions
from critiquebrainz.db.review import reviewed_entities, ENTITY_TYPES as CB_ENTITIES
from critiquebrainz.frontend.external.musicbrainz_db import special_entities

# Entity models
ENTITY_MODELS = {
    'artist': models.Artist,
    'place': models.Place,
    'release_group': models.ReleaseGroup,
    'release': models.Release,
    'event': models.Event,
    'series': models.Series,
    'url': models.URL,
}

# Redirect models
REDIRECT_MODELS = {
    'place': models.PlaceGIDRedirect,
    'artist': models.ArtistGIDRedirect,
    'release': models.ReleaseGIDRedirect,
    'release_group': models.ReleaseGroupGIDRedirect,
    'event': models.EventGIDRedirect,
}


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


def get_entities_by_gids(*, query, entity_type, mbids):
    """Get entities using their MBIDs.

    An entity can have multiple MBIDs. This function may be passed another
    MBID of an entity, in which case, it is redirected to the original entity.

    Note that the query may be modified before passing it to this
    function in order to save queries made to the database.

    Args:
        query (Query): SQLAlchemy Query object.
        entity_type (str): Type of entity being queried.
        mbids (list): IDs of the target entities.

    Returns:
        Dictionary of objects of target entities keyed by their MBID.
    """
    entity_model = ENTITY_MODELS[entity_type]
    results = query.filter(entity_model.gid.in_(mbids)).all()
    remaining_gids = list(set(mbids) - {entity.gid for entity in results})
    entities = {str(entity.gid): entity for entity in results}
    if remaining_gids:
        redirect_model = REDIRECT_MODELS[entity_type]
        query = query.add_entity(redirect_model).join(redirect_model)
        results = query.filter(redirect_model.gid.in_(remaining_gids))
        for entity, redirect_obj in results:
            entities[redirect_obj.gid] = entity
        remaining_gids = list(set(remaining_gids) - {redirect_obj.gid for entity, redirect_obj in results})

    if remaining_gids and entity_type in CB_ENTITIES:
        reviewed_gids = reviewed_entities(
            entity_ids=remaining_gids,
            entity_type=entity_type,
        )
        for entity_id in reviewed_gids:
            entities[entity_id] = unknown_entity(entity_id, entity_type)
        remaining_gids = list(set(remaining_gids) - set(reviewed_gids))

    if remaining_gids:
        raise mb_exceptions.NoDataFoundException(
            "Couldn't find entities with IDs: {mbids}".format(mbids=remaining_gids))
    return entities
