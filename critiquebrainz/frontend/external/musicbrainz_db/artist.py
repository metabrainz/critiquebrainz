from brainzutils import cache
from brainzutils.musicbrainz_db import artist as db
from brainzutils.musicbrainz_db import serialize
from brainzutils.musicbrainz_db import unknown_entities

from critiquebrainz.frontend.external.musicbrainz_db import DEFAULT_CACHE_EXPIRATION
from critiquebrainz.frontend.external.relationships import artist as artist_rel


def artist_is_unknown(artist):
    return artist == serialize.serialize_artists(unknown_entities.unknown_artist)


def get_artist_by_id(mbid):
    """Get artist with MusicBrainz ID.

    Args:
        mbid (uuid): MBID(gid) of the artist.
    Returns:
        Dictionary containing the artist information
    """
    key = cache.gen_key('artist', mbid)
    artist = cache.get(key)
    if not artist:
        artist = db.get_artist_by_id(
            mbid,
            includes=['artist-rels', 'url-rels'],
            unknown_entities_for_missing=True,
        )
        if artist_is_unknown(artist):
            return None
        cache.set(key=key, val=artist, time=DEFAULT_CACHE_EXPIRATION)
    return artist_rel.process(artist)
