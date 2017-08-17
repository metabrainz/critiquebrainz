from collections import defaultdict
from mbdata import models
from critiquebrainz.frontend.external.musicbrainz_db import mb_session, DEFAULT_CACHE_EXPIRATION
from critiquebrainz.frontend.external.musicbrainz_db.utils import get_entities_by_gids
from critiquebrainz.frontend.external.musicbrainz_db.includes import check_includes
from critiquebrainz.frontend.external.musicbrainz_db.serialize import to_dict_events
from critiquebrainz.frontend.external.musicbrainz_db.helpers import get_relationship_info
from brainzutils import cache


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
        event = _get_event_by_id(mbid)
        cache.set(key=key, val=event, time=DEFAULT_CACHE_EXPIRATION)
    return event


def _get_event_by_id(mbid):
    return fetch_multiple_events(
        [mbid],
        includes=['artist-rels', 'place-rels', 'series-rels', 'url-rels', 'release-group-rels'],
    ).get(mbid)


def fetch_multiple_events(mbids, *, includes=None):
    """Get info related to multiple events using their MusicBrainz IDs.

    Args:
        mbids (list): List of MBIDs of events.
        includes (list): List of information to be included.

    Returns:
        Dictionary containing info of multiple events keyed by their mbid.
    """
    if includes is None:
        includes = []
    includes_data = defaultdict(dict)
    check_includes('event', includes)
    with mb_session() as db:
        query = db.query(models.Event)
        events = get_entities_by_gids(
            query=query,
            entity_type='event',
            mbids=mbids,
        )
        event_ids = [event.id for event in events.values()]

        if 'artist-rels' in includes:
            get_relationship_info(
                db=db,
                target_type='artist',
                source_type='event',
                source_entity_ids=event_ids,
                includes_data=includes_data,
            )
        if 'place-rels' in includes:
            get_relationship_info(
                db=db,
                target_type='place',
                source_type='event',
                source_entity_ids=event_ids,
                includes_data=includes_data,
            )
        if 'series-rels' in includes:
            get_relationship_info(
                db=db,
                target_type='series',
                source_type='event',
                source_entity_ids=event_ids,
                includes_data=includes_data,
            )
        if 'url-rels' in includes:
            get_relationship_info(
                db=db,
                target_type='url',
                source_type='event',
                source_entity_ids=event_ids,
                includes_data=includes_data,
            )
        if 'release-group-rels' in includes:
            get_relationship_info(
                db=db,
                target_type='release_group',
                source_type='event',
                source_entity_ids=event_ids,
                includes_data=includes_data,
            )
    return {str(mbid): to_dict_events(events[mbid], includes_data[events[mbid].id]) for mbid in mbids}
