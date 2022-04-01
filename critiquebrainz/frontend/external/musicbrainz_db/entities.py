from brainzutils.musicbrainz_db.artist import fetch_multiple_artists
from brainzutils.musicbrainz_db.event import fetch_multiple_events
from brainzutils.musicbrainz_db.label import fetch_multiple_labels
from brainzutils.musicbrainz_db.place import fetch_multiple_places
from brainzutils.musicbrainz_db.release_group import fetch_multiple_release_groups
from brainzutils.musicbrainz_db.work import fetch_multiple_works
from brainzutils.musicbrainz_db.recording import fetch_multiple_recordings

from critiquebrainz.frontend.external.musicbrainz_db import artist
from critiquebrainz.frontend.external.musicbrainz_db import event
from critiquebrainz.frontend.external.musicbrainz_db import label
from critiquebrainz.frontend.external.musicbrainz_db import place
from critiquebrainz.frontend.external.musicbrainz_db import release_group
from critiquebrainz.frontend.external.musicbrainz_db import work
from critiquebrainz.frontend.external.musicbrainz_db import recording


def get_multiple_entities(entities):
    """Fetch multiple entities using their MBIDs.

    Args:
        entities: List of tuples containing the entity ID and the entity type.

    Returns:
        Dictionary containing the basic information related to the entities.
        {
            "[entity_id]":
                {
                    "id": uuid,
                    "name/title": str,
                }
        }
        Information related to the artists of release groups and the
        coordinates of the places is also included.
    """
    entities_info = {}
    release_group_mbids = [entity[0] for entity in entities if entity[1] == 'release_group']
    artist_mbids = [entity[0] for entity in entities if entity[1] == 'artist']
    label_mbids = [entity[0] for entity in entities if entity[1] == 'label']
    recording_mbids = [entity[0] for entity in entities if entity[1] == 'recording']
    place_mbids = [entity[0] for entity in entities if entity[1] == 'place']
    event_mbids = [entity[0] for entity in entities if entity[1] == 'event']
    work_mbids = [entity[0] for entity in entities if entity[1] == 'work']

    release_groups = fetch_multiple_release_groups(
        release_group_mbids,
        includes=['artists'],
        unknown_entities_for_missing=True,
    )
    release_groups = {id: rg for id, rg in release_groups.items() if not release_group.release_group_is_unknown(rg)}
    entities_info.update(release_groups)
    artists = fetch_multiple_artists(
        artist_mbids,
    )
    artists = {id: a for id, a in artists.items() if not artist.artist_is_unknown(a)}
    entities_info.update(artists)
    labels = fetch_multiple_labels(
        label_mbids,
    )
    labels = {id: l for id, l in labels.items() if not label.label_is_unknown(l)}
    entities_info.update(labels)
    places = fetch_multiple_places(
        place_mbids,
        unknown_entities_for_missing=True,
    )
    places = {id: p for id, p in places.items() if not place.place_is_unknown(p)}
    entities_info.update(places)
    events = fetch_multiple_events(
        event_mbids,
        unknown_entities_for_missing=True,
    )
    events = {id: e for id, e in events.items() if not event.event_is_unknown(e)}
    entities_info.update(events)
    works = fetch_multiple_works(
        work_mbids,
    )
    works = {id: w for id, w in works.items() if not work.work_is_unknown(w)}
    entities_info.update(works)
    recordings = fetch_multiple_recordings(
        recording_mbids,
    )
    recordings = {id: r for id, r in recordings.items() if not recording.recording_is_unknown(r)}
    entities_info.update(recordings)
    return entities_info


def get_entity_by_id(id, type='release_group'):
    """A wrapper to call the correct get_*_by_id function."""
    if type == 'release_group':
        entity = release_group.get_release_group_by_id(str(id))
    elif type == 'artist':
        entity = artist.get_artist_by_id(str(id))
    elif type == 'label':
        entity = label.get_label_by_id(str(id))
    elif type == 'place':
        entity = place.get_place_by_id(str(id))
    elif type == 'event':
        entity = event.get_event_by_id(str(id))
    elif type == 'work':
        entity = work.get_work_by_id(str(id))
    elif type == 'recording':
        entity = recording.get_recording_by_id(str(id))
    return entity


def entity_is_unknown(entity, entity_type):
    """A wrapper to call the correct get_*_by_id function."""
    if entity_type == 'release_group':
        return release_group.release_group_is_unknown(entity)
    elif entity_type == 'artist':
        return artist.artist_is_unknown(entity)
    elif entity_type == 'label':
        return label.label_is_unknown(entity)
    elif entity_type == 'place':
        return place.place_is_unknown(entity)
    elif entity_type == 'event':
        return event.event_is_unknown(entity)
    elif entity_type == 'work':
        return work.work_is_unknown(entity)
    elif entity_type == 'recording':
        return recording.recording_is_unknown(entity)
    else:
        raise ValueError("Unexpected entity_type")
