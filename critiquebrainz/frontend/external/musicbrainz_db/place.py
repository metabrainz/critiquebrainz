from mbdata import models
from mbdata.utils import get_something_by_gid
from critiquebrainz.frontend.external.musicbrainz_db import mb_session
from critiquebrainz.frontend.external.musicbrainz_db.includes import check_includes
import critiquebrainz.frontend.external.musicbrainz_db.exceptions as mb_exceptions
from critiquebrainz.frontend.external.musicbrainz_db.serialize import to_dict_places
from critiquebrainz.frontend.external.musicbrainz_db.helpers import entity_relation_helper
from critiquebrainz.frontend.external.relationships import place as place_rel
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
        place = _get_place_by_id(
            mbid, includes=['artist-rels', 'place-rels', 'release-group-rels', 'url-rels'],
        )
    cache.set(key=key, val=place, time=DEFAULT_CACHE_EXPIRATION)
    return place_rel.process(place)


def _get_place_by_id(place_id, includes=None):
    if includes is None:
        includes = []
    includes_data = {}
    check_includes('place', includes)
    with mb_session() as db:
        query = db.query(models.Place)
        place = get_something_by_gid(query, models.PlaceGIDRedirect, place_id)
        if not place:
            raise mb_exceptions.NoDataFoundException("Couldn't find a place with id: {place_id}".format(place_id=place_id))

        if 'artist-rels' in includes:
            includes_data.setdefault('relationship_objs', {})['artist-rels'] = entity_relation_helper(db, 'artist', 'place', place.id)
        if 'place-rels' in includes:
            includes_data.setdefault('relationship_objs', {})['place-rels'] = entity_relation_helper(db, 'place', 'place', place.id)
        if 'url-rels' in includes:
            includes_data.setdefault('relationship_objs', {})['url-rels'] = entity_relation_helper(db, 'url', 'place', place.id)

        place = to_dict_places(place, includes_data)
    return place
