from mbdata import models
from mbdata.utils import get_something_by_gid
from critiquebrainz.frontend.external.musicbrainz_db import mb_session
from critiquebrainz.frontend.external.musicbrainz_db.includes import check_includes
import critiquebrainz.frontend.external.musicbrainz_db.exceptions as mb_exceptions
from critiquebrainz.frontend.external.musicbrainz_db.serialize import to_dict_places
from critiquebrainz.frontend.external.musicbrainz_db.helpers import entity_relation_helper
from critiquebrainz.frontend.external.relationships import place as place_rel
from collections import defaultdict
from brainzutils import cache


DEFAULT_CACHE_EXPIRATION = 12 * 60 * 60 # seconds (12 hours)
THREAD_POOL_PROCESSES = 10


def get_place_by_id(mbid):
    """Get place with the MusicBrainz ID.

    Args:
        mbid (uuid): MBID(gid) of the place.
    Returns:
        Dictionary containing the place information.
    """
    key = cache.gen_key(mbid)
    place = cache.get(key)
    if not place:
        place = fetch_multiple_places(
            mbids=[mbid],
            includes=['artist-rels', 'place-rels', 'release-group-rels', 'url-rels'],
        ).get(mbid)
    cache.set(key=key, val=place, time=DEFAULT_CACHE_EXPIRATION)
    return place_rel.process(place)


def fetch_multiple_places(*, mbids, includes=None):
    """Get info related to multiple places using their MusicBrainz IDs.

    Args:
        mbids (list): List of MBIDs of places.
        includes (list): List of information to be included.

    Returns:
        Dictionary containing info of multiple places keyed by their mbid.
    """
    if includes is None:
        includes = []
    includes_data = defaultdict(dict)
    check_includes('place', includes)
    with mb_session() as db:
        query = db.query(models.Place)
        places = []
        for mbid in mbids:
            place = get_something_by_gid(query, models.PlaceGIDRedirect, mbid)
            if not place:
                raise mb_exceptions.NoDataFoundException("Couldn't find a place with id: {mbid}".format(mbid=mbid))
            places.append(place)
        place_ids = [place.id for place in places]

        if 'artist-rels' in includes:
            entity_relation_helper(db, 'artist', 'place', place_ids, includes_data)
        if 'place-rels' in includes:
            entity_relation_helper(db, 'place', 'place', place_ids, includes_data)
        if 'url-rels' in includes:
            entity_relation_helper(db, 'url', 'place', place_ids, includes_data)

        places = {str(place.gid): to_dict_places(place, includes_data[place.id]) for place in places}
    return places
