from brainzutils import cache
from brainzutils.musicbrainz_db import place as db

from critiquebrainz.frontend.external.musicbrainz_db import DEFAULT_CACHE_EXPIRATION
from critiquebrainz.frontend.external.relationships import place as place_rel


def get_place_by_id(mbid):
    """Get place with the MusicBrainz ID.

    Args:
        mbid (uuid): MBID(gid) of the place.
    Returns:
        Dictionary containing the place information.
    """
    key = cache.gen_key('place', mbid)
    place = cache.get(key)
    if not place:
        place = db.fetch_multiple_places(
            [mbid],
            includes=['artist-rels', 'place-rels', 'release-group-rels', 'url-rels'],
            unknown_entities_for_missing=True,
        ).get(mbid)
        cache.set(key=key, val=place, time=DEFAULT_CACHE_EXPIRATION)
    return place_rel.process(place)
