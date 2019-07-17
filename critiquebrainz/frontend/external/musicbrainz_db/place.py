from brainzutils import cache
from brainzutils.musicbrainz_db.place import fetch_multiple_places as get_places_by_gids
from critiquebrainz.frontend.external.musicbrainz_db import DEFAULT_CACHE_EXPIRATION
from critiquebrainz.frontend.external.relationships import place as place_rel
from critiquebrainz.frontend.external.musicbrainz_db.utils import map_deleted_mb_entities_to_unknown


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


def fetch_multiple_places(mbids, includes=None):
    multiple_places = get_places_by_gids(
        mbids,
        includes=includes,
        suppress_no_data_found=True,
    )
    places_mapped_to_unknown = map_deleted_mb_entities_to_unknown(
        entities=multiple_places,
        entity_type="place",
        mbids=mbids
    )
    return places_mapped_to_unknown
