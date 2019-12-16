from brainzutils import cache
from brainzutils.musicbrainz_db.work import fetch_multiple_works
from critiquebrainz.frontend.external.musicbrainz_db import DEFAULT_CACHE_EXPIRATION


def get_work_by_id(mbid):
    """Get work with MusicBrainz ID.

    Args:
        mbid (uuid): MBID(gid) of the work.
    Returns:
        Dictionary containing the work information
    """
    key = cache.gen_key(mbid)
    work = cache.get(key)
    if not work:
        work = fetch_multiple_works(
            [mbid],
            includes=['artist-rels', 'recording-rels'],
        ).get(mbid)
        cache.set(key=key, val=work, time=DEFAULT_CACHE_EXPIRATION)
    return work
