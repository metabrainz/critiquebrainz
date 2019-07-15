from brainzutils import cache
from brainzutils.musicbrainz_db.place import fetch_multiple_places
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
        multiple_places = fetch_multiple_places(
            [mbid],
            includes=['artist-rels', 'place-rels', 'release-group-rels', 'url-rels'],
        )
        place = map_deleted_mb_entities_to_unknown(
            entities=multiple_places,
            entity_type="place",
            mbids=[mbid]
        ).get(mbid)
        cache.set(key=key, val=place, time=DEFAULT_CACHE_EXPIRATION)
    return place_rel.process(place)
