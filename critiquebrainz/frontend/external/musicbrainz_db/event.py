from brainzutils import cache
from brainzutils.musicbrainz_db import event as db
from brainzutils.musicbrainz_db import serialize
from brainzutils.musicbrainz_db import unknown_entities

from critiquebrainz.frontend.external.musicbrainz_db import DEFAULT_CACHE_EXPIRATION


def event_is_unknown(event):
    return event == serialize.serialize_events(unknown_entities.unknown_event)


def get_event_by_id(mbid):
    """Get event with the MusicBrainz ID.

    Args:
        mbid (uuid): MBID(gid) of the event.
    Returns:
        Dictionary containing the event information.
    """
    key = cache.gen_key('event', mbid)
    event = cache.get(key)
    if not event:
        event = db.get_event_by_id(
            mbid,
            includes=['artist-rels', 'place-rels', 'series-rels', 'url-rels', 'release-group-rels'],
            unknown_entities_for_missing=True,
        )
        if event_is_unknown(event):
            return None
        cache.set(key, event, DEFAULT_CACHE_EXPIRATION)
    return event
