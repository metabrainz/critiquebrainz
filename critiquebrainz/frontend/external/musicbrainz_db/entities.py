from brainzutils.musicbrainz_db.recording import fetch_multiple_recordings
from brainzutils.musicbrainz_db.artist import fetch_multiple_artists
from brainzutils.musicbrainz_db.label import fetch_multiple_labels
from brainzutils.musicbrainz_db.place import fetch_multiple_places
from brainzutils.musicbrainz_db.event import fetch_multiple_events
from brainzutils.musicbrainz_db.release_group import fetch_multiple_release_groups
from critiquebrainz.frontend.external.musicbrainz_db.release_group import get_release_group_by_id
from critiquebrainz.frontend.external.musicbrainz_db.place import get_place_by_id
from critiquebrainz.frontend.external.musicbrainz_db.event import get_event_by_id
from critiquebrainz.frontend.external.musicbrainz_db.label import get_label_by_id
from critiquebrainz.frontend.external.musicbrainz_db.artist import get_artist_by_id
from critiquebrainz.frontend.external.musicbrainz_db.recording import get_recording_by_id


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
    artist_mbids = [entity[0] for entity in filter(lambda entity: entity[1] == 'artist', entities)]
    recording_mbids = [entity[0] for entity in filter(lambda entity: entity[1] == 'recording', entities)]
    label_mbids = [entity[0] for entity in filter(lambda entity: entity[1] == 'label', entities)]
    place_mbids = [entity[0] for entity in filter(lambda entity: entity[1] == 'place', entities)]
    event_mbids = [entity[0] for entity in filter(lambda entity: entity[1] == 'event', entities)]
    entities_info.update(fetch_multiple_release_groups(
        release_group_mbids,
        includes=['artists'],
    ))
    entities_info.update(fetch_multiple_artists(
        artist_mbids,
    ))
    entities_info.update(fetch_multiple_recordings(
        recording_mbids,
    ))
    entities_info.update(fetch_multiple_labels(
        label_mbids,
    ))
    entities_info.update(fetch_multiple_places(
        place_mbids,
    ))
    entities_info.update(fetch_multiple_events(
        event_mbids,
    ))
    return entities_info


def get_entity_by_id(id, type='release_group'):
    """A wrapper to call the correct get_*_by_id function."""
    if type == 'release_group':
        entity = get_release_group_by_id(str(id))
    elif type == 'artist':
        entity = get_artist_by_id(str(id))
    elif type == 'recording':
        entity = get_recording_by_id(str(id))
    elif type == 'label':
        entity = get_label_by_id(str(id))
    elif type == 'place':
        entity = get_place_by_id(str(id))
    elif type == 'event':
        entity = get_event_by_id(str(id))
    return entity
