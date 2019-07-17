from brainzutils import cache
from brainzutils.musicbrainz_db.artist import fetch_multiple_artists as get_artists_by_gids
from critiquebrainz.frontend.external.musicbrainz_db import DEFAULT_CACHE_EXPIRATION
from critiquebrainz.frontend.external.relationships import artist as artist_rel
from critiquebrainz.frontend.external.musicbrainz_db.utils import map_deleted_mb_entities_to_unknown


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


def fetch_multiple_artists(mbids, includes=None):
    multiple_artists = get_artists_by_gids(
        mbids,
        includes=includes,
        suppress_no_data_found=True,
    )
    artists_mapped_to_unknown = map_deleted_mb_entities_to_unknown(
        entities=multiple_artists,
        entity_type="artist",
        mbids=mbids,
    )
    return artists_mapped_to_unknown
