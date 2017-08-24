from critiquebrainz.frontend.external.musicbrainz_db.release_group import fetch_multiple_release_groups, get_release_group_by_id
from critiquebrainz.frontend.external.musicbrainz_db.place import fetch_multiple_places, get_place_by_id
from critiquebrainz.frontend.external.musicbrainz_db.event import fetch_multiple_events, get_event_by_id


def get_multiple_entities(entities):
    """Fetch multiple entities using their mbids.

    Args:
        entites: List of tuples containing the entity_id and the entity_type.

    Returns:
        Dictionary containing the entities keyed by their mbid.
    """
    entities_info = {}
    release_group_mbids = [entity[0] for entity in filter(lambda entity: entity[1] == 'release_group', entities)]
    place_mbids = [entity[0] for entity in filter(lambda entity: entity[1] == 'place', entities)]
    event_mbids = [entity[0] for entity in filter(lambda entity: entity[1] == 'event', entities)]
    if release_group_mbids:
        release_groups = fetch_multiple_release_groups(
            release_group_mbids,
            includes=['artists'],
        )
        entities_info.update(release_groups)
    if place_mbids:
        places = fetch_multiple_places(
            place_mbids,
        )
        entities_info.update(places)
    if event_mbids:
        events = fetch_multiple_events(
            event_mbids,
        )
        entities_info.update(events)
    return entities_info


def get_entity_by_id(id, type='release_group'):
    """A wrapper to call the correct get_*_by_id function."""
    if type == 'release_group':
        entity = get_release_group_by_id(id)
    elif type == 'place':
        entity = get_place_by_id(id)
    elif type == 'event':
        entity = get_event_by_id(id)
    return entity
