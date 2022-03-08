from brainzutils import cache
from brainzutils.musicbrainz_db import event as db

from critiquebrainz.frontend.external.musicbrainz_db import DEFAULT_CACHE_EXPIRATION


def get_event_by_mbid(mbid):
    """Get event with the MusicBrainz ID.

    Args:
        mbid (uuid): MBID(gid) of the event.
    Returns:
        Dictionary containing the event information.
    """
    key = cache.gen_key('event', mbid)
    event = cache.get(key)
    if not event:
        event = db.get_event_by_mbid(
            mbid,
            includes=['artist-rels', 'place-rels', 'series-rels', 'url-rels', 'release-group-rels'],
        )
        if not event:
            return None
        cache.set(key, event, DEFAULT_CACHE_EXPIRATION)
    return event
