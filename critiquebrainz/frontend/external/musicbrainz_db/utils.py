import critiquebrainz.frontend.external.musicbrainz_db.exceptions as mb_exceptions
from mbdata import models


# Entity models
ENTITY_MODELS = {
    'artist': models.Artist,
    'place': models.Place,
    'release_group': models.ReleaseGroup,
    'release': models.Release,
    'event': models.Event,
}


# Redirect models
REDIRECT_MODELS = {
    'place': models.PlaceGIDRedirect,
    'artist': models.ArtistGIDRedirect,
    'release': models.ReleaseGIDRedirect,
    'release_group': models.ReleaseGroupGIDRedirect,
    'event': models.EventGIDRedirect,
}


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
        List of objects of target entities.
    """
    entity_model = ENTITY_MODELS[entity_type]
    redirect_model = REDIRECT_MODELS[entity_type]
    entities = query.filter(entity_model.gid.in_(mbids)).all()
    remaining_gids = list(set(mbids) - {entity.gid for entity in entities})
    if remaining_gids:
        redirects = query.session.query(redirect_model).filter(redirect_model.gid.in_(remaining_gids))
        redirect_gids = {redirect.redirect_id: redirect.gid for redirect in redirects}
        redirected_entities = query.filter(redirect_model.redirect.property.primaryjoin.left.in_(redirect_gids.keys())).all()
        for entity in redirected_entities:
            entity.gid = redirect_gids[entity.id]
        entities.extend(redirected_entities)
    remaining_gids = list(set(mbids) - {entity.gid for entity in entities})
    if remaining_gids:
        raise mb_exceptions.NoDataFoundException("Couldn't find entities with IDs: {mbids}".format(mbids=remaining_gids))
    return entities
