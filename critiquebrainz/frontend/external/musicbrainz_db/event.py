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


def get_event_for_place(place_id, event_types=None, limit=None, offset=None, includeNullType = False):
    """Get events for the place.

    Args:
        place_id (uuid): MBID(gid) of the place.
        event_types (list): List of event types to be fetched.
        limit (int): Max number of events to return.
        offset (int): Offset that can be used in conjunction with the limit.
        includeNullType (bool): If True, include events with null event type.

    Returns:
        Tuple containing the list of dictionaries of events ordered by begin year
        and the total count of the events.
    """
    key = cache.gen_key( place_id, limit, offset, includeNullType, *event_types)
    events = cache.get(key)
    if not events:
        events = db.get_event_for_place(
            place_id,
            event_types=event_types,
            limit=limit,
            offset=offset,
            includeNullType = includeNullType,
        )
        if not events:
            return None
        cache.set(key, events, DEFAULT_CACHE_EXPIRATION)
    return events
