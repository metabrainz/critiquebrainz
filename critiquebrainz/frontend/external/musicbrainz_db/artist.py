from brainzutils import cache
from brainzutils.musicbrainz_db.artist import fetch_multiple_artists

from critiquebrainz.frontend.external.musicbrainz_db import DEFAULT_CACHE_EXPIRATION
from critiquebrainz.frontend.external.relationships import artist as artist_rel


def get_artist_by_id(mbid):
    """Get artist with MusicBrainz ID.

    Args:
        mbid (uuid): MBID(gid) of the artist.
    Returns:
        Dictionary containing the artist information
    """
    key = cache.gen_key(mbid)
    artist = cache.get(key)
    if not artist:
        artist = fetch_multiple_artists(
            [mbid],
            includes=['artist-rels', 'url-rels'],
        ).get(mbid)
        cache.set(key=key, val=artist, time=DEFAULT_CACHE_EXPIRATION)
    return artist_rel.process(artist)
