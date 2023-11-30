"""
This package (api) provides modules to access external services:
 - MusicBrainz (with advanced relationship support)
 - Spotify
 - mbspotify

See documentation in each module for information about usage.
"""
from flask import current_app, _app_ctx_stack

from critiquebrainz.frontend.external.entities import get_entity_by_id, get_multiple_entities


class MBDataAccess(object):
    """A data access object which switches between database get methods or development versions
    This is useful because we won't show a review if we cannot find its metadata in the
    musicbrainz database. If a developer is using the musicbrainz sample database (for size reasons)
    then they will only be able to see very few reviews.
    During development mode, we replace the access methods (get_entity_by_id and get_multiple_entities)
    with a development version which always returns some dummy metadata so that reviews are always shown.
    """
    def __init__(self, app=None):
        self.app = app
        if app:
            self.init_app(self.app)

    def init_app(self, app):
        if self.app is None:
            self.app = app

        from critiquebrainz.frontend.external.entities import get_entity_by_id, get_multiple_entities
        if self.app.config["DEBUG"]:
            self.get_entity_by_id_method = development_get_entity_by_id
            self.get_multiple_entities_method = development_get_multiple_entities
        else:
            self.get_entity_by_id_method = get_entity_by_id
            self.get_multiple_entities_method = get_multiple_entities

    @property
    def get_entity_by_id(self):
        ctx = _app_ctx_stack.top
        if ctx is not None:
            if not hasattr(ctx, 'get_entity_by_id'):
                ctx.get_entity_by_id = self.get_entity_by_id_method
            return ctx.get_entity_by_id

    @property
    def get_multiple_entities(self):
        ctx = _app_ctx_stack.top
        if ctx is not None:
            if not hasattr(ctx, 'get_multiple_entities'):
                ctx.get_multiple_entities = self.get_multiple_entities_method
            return ctx.get_multiple_entities


mbstore = MBDataAccess()


def development_get_multiple_entities(entities):
    """Same as get_multiple_entities, but always returns items for all entities even if one
    isn't in the MusicBrainz database. Used in development with a sample database."""
    data = get_multiple_entities(entities)
    missing_entities = [(mbid, entity_type) for mbid, entity_type in entities if mbid not in data]
    if missing_entities:
        current_app.logger.info("returning dummy entities in development mode")
    for mbid, entity_type in missing_entities:
        data[mbid] = get_dummy_item(mbid, entity_type)
    return data

def development_get_entity_by_id(entity_id, entity_type):
    """Same as get_entity_by_id, but always returns a dummy item if the requested entity
       isn't in the MusicBrainz database. Used in development with a sample database."""
    entity = get_entity_by_id(entity_id, entity_type)
    if entity is None and current_app.config["DEBUG"]:
        current_app.logger.info("returning dummy entity in development mode")
        return get_dummy_item(entity_id, entity_type)
    return entity


def get_dummy_item(entity_id, entity_type):
    """Get something that looks just enough like a MusicBrainz entity to display in a CB template"""
    if entity_type.startswith("bb_"):
        return {
            "bbid": entity_id,
            "title": entity_type + " missing from sample database",
            "name": entity_type + " missing from sample database",
            "disambiguation": "This dummy item exists if DEBUG=True so that the review can be viewed",
        }

    return {"mbid": entity_id,
            "title": entity_type + " missing from sample database",
            "name": entity_type + " missing from sample database",
            "artist-credit-phrase": "Artist",
            "artist-credit": [{"artist": {"mbid": "6a0b0138-dc06-4d5c-87b3-fab64f0fd326", "name": "No one"}}],
            "comment": "This dummy item exists if DEBUG=True so that the review can be viewed"}
