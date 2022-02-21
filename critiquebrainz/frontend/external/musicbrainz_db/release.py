from brainzutils import cache
from brainzutils.musicbrainz_db import release as db

from critiquebrainz.frontend.external.musicbrainz_db import DEFAULT_CACHE_EXPIRATION


def get_release_by_id(mbid):
    """Get release with MusicBrainz ID.

    Args:
        mbid (uuid): MBID(gid) of the release.
    Returns:
        Dictionary containing the release information
    """
    key = cache.gen_key('release', mbid)
    release = cache.get(key)
    if not release:
        release = db.get_release_by_id(
            mbid,
            includes=['media', 'release-groups'],
            unknown_entities_for_missing=True,
        )
        cache.set(key, release, DEFAULT_CACHE_EXPIRATION)
    return release
