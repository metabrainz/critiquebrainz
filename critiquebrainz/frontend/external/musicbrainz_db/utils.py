import critiquebrainz.frontend.external.musicbrainz_db.exceptions as mb_exceptions


def get_entities_by_gids(query, entity_model, redirect_model, mbids):
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
        raise mb_exceptions.NoDataFoundException("Couldn't find an entity with id(s): {mbids}".format(mbids=remaining_gids))
    return entities
