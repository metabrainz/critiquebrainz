from collections import defaultdict
from mbdata import models
from sqlalchemy.orm import joinedload
from brainzutils import cache
from critiquebrainz.frontend.external.musicbrainz_db import mb_session
from critiquebrainz.frontend.external.musicbrainz_db.includes import check_includes
from critiquebrainz.frontend.external.musicbrainz_db.serialize import to_dict_places
from critiquebrainz.frontend.external.musicbrainz_db.helpers import get_relationship_info
from critiquebrainz.frontend.external.relationships import place as place_rel
from critiquebrainz.frontend.external.musicbrainz_db.utils import get_entities_by_gids


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
            [mbid],
            includes=['artist-rels', 'place-rels', 'release-group-rels', 'url-rels'],
        ).get(mbid)
    cache.set(key=key, val=place, time=DEFAULT_CACHE_EXPIRATION)
    return place_rel.process(place)


def fetch_multiple_places(mbids, *, includes=None):
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
        query = db.query(models.Place).\
                options(joinedload("area")).\
                options(joinedload("type"))
        places = get_entities_by_gids(query, models.Place, models.PlaceGIDRedirect, mbids)
        place_ids = [place.id for place in places]

        if 'artist-rels' in includes:
            get_relationship_info(
                db=db,
                target_type='artist',
                source_type='place',
                source_entity_ids=place_ids,
                includes_data=includes_data,
            )
        if 'place-rels' in includes:
            get_relationship_info(
                db=db,
                target_type='place',
                source_type='place',
                source_entity_ids=place_ids,
                includes_data=includes_data,
            )
        if 'url-rels' in includes:
            get_relationship_info(
                db=db,
                target_type='url',
                source_type='place',
                source_entity_ids=place_ids,
                includes_data=includes_data,
            )

        places = {str(place.gid): to_dict_places(place, includes_data[place.id]) for place in places}
    return places
