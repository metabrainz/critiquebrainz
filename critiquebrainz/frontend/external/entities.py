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
from critiquebrainz.frontend.external.bookbrainz_db import edition_group
from critiquebrainz.frontend.external.bookbrainz_db import author


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
    edition_group_bbids = [entity[0] for entity in entities if entity[1] == 'bb_edition_group']
    author_bbids = [entity[0] for entity in entities if entity[1] == 'bb_author']

    release_groups = fetch_multiple_release_groups(
        release_group_mbids,
        includes=['artists'],
    )
    entities_info.update(release_groups)
    artists = fetch_multiple_artists(
        artist_mbids,
    )
    entities_info.update(artists)
    labels = fetch_multiple_labels(
        label_mbids,
    )
    entities_info.update(labels)
    places = fetch_multiple_places(
        place_mbids,
    )
    entities_info.update(places)
    events = fetch_multiple_events(
        event_mbids,
    )
    entities_info.update(events)
    works = fetch_multiple_works(
        work_mbids,
    )
    entities_info.update(works)
    recordings = fetch_multiple_recordings(
        recording_mbids,
        includes=['artists'],
    )
    entities_info.update(recordings)
    edition_groups = edition_group.fetch_multiple_edition_groups(
        edition_group_bbids,
    )
    entities_info.update(edition_groups)
    authors = author.fetch_multiple_authors(
        author_bbids,
    )
    entities_info.update(authors)
    
    return entities_info


def get_entity_by_id(id, entity_type):
    """A wrapper to call the correct get_*_by_mbid function."""
    if entity_type == 'release_group':
        entity = release_group.get_release_group_by_mbid(str(id))
    elif entity_type == 'artist':
        entity = artist.get_artist_by_mbid(str(id))
    elif entity_type == 'label':
        entity = label.get_label_by_mbid(str(id))
    elif entity_type == 'place':
        entity = place.get_place_by_mbid(str(id))
    elif entity_type == 'event':
        entity = event.get_event_by_mbid(str(id))
    elif entity_type == 'work':
        entity = work.get_work_by_mbid(str(id))
    elif entity_type == 'recording':
        entity = recording.get_recording_by_mbid(str(id))
    elif entity_type == 'bb_edition_group':
        entity = edition_group.get_edition_group_by_bbid(str(id))
    else:
        raise ValueError('Unknown entity type')
    return entity
