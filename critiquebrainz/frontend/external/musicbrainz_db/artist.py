from brainzutils import cache
from brainzutils.musicbrainz_db import artist as db

from critiquebrainz.frontend.external.musicbrainz_db import DEFAULT_CACHE_EXPIRATION
from critiquebrainz.frontend.external.relationships import artist as artist_rel


def get_artist_by_mbid(mbid):
    """Get artist with MusicBrainz ID.

    Args:
        mbid (uuid): MBID(gid) of the artist.
    Returns:
        Dictionary containing the artist information
    """
    key = cache.gen_key('artist', mbid)
    artist = cache.get(key)
    if not artist:
        artist = db.get_artist_by_mbid(
            mbid,
            includes=['artist-rels', 'url-rels'],
        )
        if not artist:
            return None
        cache.set(key, artist, DEFAULT_CACHE_EXPIRATION)
    return artist_rel.process(artist)
