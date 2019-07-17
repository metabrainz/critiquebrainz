from brainzutils import cache
from brainzutils.musicbrainz_db.release import fetch_multiple_releases as get_releases_by_gids
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
        release = fetch_multiple_releases(
            [mbid],
            includes=['media', 'release-groups'],
        ).get(mbid)
        cache.set(key=key, val=release, time=DEFAULT_CACHE_EXPIRATION)
    return release


def fetch_multiple_releases(mbids, includes=None):
    multiple_releases = get_releases_by_gids(
        mbids,
        includes=includes,
        suppress_no_data_found=True,
    )
    releases_mapped_to_unknown = map_deleted_mb_entities_to_unknown(
        entities=multiple_releases,
        entity_type="release",
        mbids=mbids,
    )
    return releases_mapped_to_unknown
