from brainzutils import cache
from brainzutils.musicbrainz_db.release import fetch_multiple_releases
from critiquebrainz.frontend.external.musicbrainz_db import DEFAULT_CACHE_EXPIRATION
from critiquebrainz.frontend.external.musicbrainz_db.utils import map_deleted_mb_entities_to_unknown


def get_release_by_id(mbid):
    """Get release with MusicBrainz ID.

    Args:
        mbid (uuid): MBID(gid) of the release.
    Returns:
        Dictionary containing the release information
    """
    key = cache.gen_key(mbid)
    release = cache.get(key)
    if not release:
        multiple_releases = fetch_multiple_releases(
            [mbid],
            includes=['media', 'release-groups'],
        )
        release = map_deleted_mb_entities_to_unknown(
            entities=multiple_releases,
            entity_type="release",
            mbids=[mbid]
        ).get(mbid)
        cache.set(key=key, val=release, time=DEFAULT_CACHE_EXPIRATION)
    return release
