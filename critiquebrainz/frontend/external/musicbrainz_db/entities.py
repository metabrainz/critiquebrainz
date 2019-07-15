from brainzutils.musicbrainz_db.place import fetch_multiple_places
from brainzutils.musicbrainz_db.event import fetch_multiple_events
from brainzutils.musicbrainz_db.release_group import fetch_multiple_release_groups
from critiquebrainz.frontend.external.musicbrainz_db.release_group import get_release_group_by_id
from critiquebrainz.frontend.external.musicbrainz_db.place import get_place_by_id
from critiquebrainz.frontend.external.musicbrainz_db.event import get_event_by_id
from critiquebrainz.frontend.external.musicbrainz_db.utils import map_deleted_mb_entities_to_unknown


def get_multiple_entities(entities):
    """Fetch multiple entities using their MBIDs.

    Args:
        entites: List of tuples containing the entity ID and the entity type.

    Returns:
        Dictionary containing the basic information related to the entities.
        {
            "id": uuid,
            "name/title": str,
        }
        Information related to the artists of release groups and the
        coordinates of the places is also included.
    """
    entities_info = {}
    release_group_mbids = [entity[0] for entity in filter(lambda entity: entity[1] == 'release_group', entities)]
    place_mbids = [entity[0] for entity in filter(lambda entity: entity[1] == 'place', entities)]
    event_mbids = [entity[0] for entity in filter(lambda entity: entity[1] == 'event', entities)]
    multiple_release_groups = fetch_multiple_release_groups(release_group_mbids, includes=['artists'])
    multiple_places = fetch_multiple_places(place_mbids)
    multiple_events = fetch_multiple_events(event_mbids)
    entities_info.update(map_deleted_mb_entities_to_unknown(
        entities=entities_info,
        entity_type="release_group",
        mbids=multiple_release_groups,
    ))
    entities_info.update(map_deleted_mb_entities_to_unknown(
        entities=entities_info,
        entity_type="place",
        mbids=multiple_places,
    ))
    entities_info.update(map_deleted_mb_entities_to_unknown(
        entities=entities_info,
        entity_type="event",
        mbids=multiple_events,
    ))
    return entities_info


def get_entity_by_id(id, type='release_group'):
    """A wrapper to call the correct get_*_by_id function."""
    if type == 'release_group':
        entity = get_release_group_by_id(str(id))
    elif type == 'place':
        entity = get_place_by_id(str(id))
    elif type == 'event':
        entity = get_event_by_id(str(id))
    return entity
