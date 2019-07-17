from brainzutils import cache
from brainzutils.musicbrainz_db.event import fetch_multiple_events as get_events_by_gids
from critiquebrainz.frontend.external.musicbrainz_db import DEFAULT_CACHE_EXPIRATION
from critiquebrainz.frontend.external.musicbrainz_db.utils import map_deleted_mb_entities_to_unknown


def get_event_by_id(mbid):
    """Get event with the MusicBrainz ID.

    Args:
        mbid (uuid): MBID(gid) of the event.
    Returns:
        Dictionary containing the event information.
    """
    key = cache.gen_key(mbid)
    event = cache.get(key)
    if not event:
        event = fetch_multiple_events(
            [mbid],
            includes=['artist-rels', 'place-rels', 'series-rels', 'url-rels', 'release-group-rels'],
        ).get(mbid)
        cache.set(key=key, val=event, time=DEFAULT_CACHE_EXPIRATION)
    return event


def fetch_multiple_events(mbids, includes=None):
    multiple_events = get_events_by_gids(
        mbids,
        includes=includes,
        suppress_no_data_found=True,
    )
    events_mapped_to_unknown = map_deleted_mb_entities_to_unknown(
        entities=multiple_events,
        entity_type="event",
        mbids=mbids,
    )
    return events_mapped_to_unknown
