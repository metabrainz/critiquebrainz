from brainzutils import cache
from brainzutils.musicbrainz_db.release_group import fetch_multiple_release_groups, get_release_groups_for_artist
from critiquebrainz.frontend.external.musicbrainz_db import DEFAULT_CACHE_EXPIRATION
import critiquebrainz.frontend.external.relationships.release_group as release_group_rel
from critiquebrainz.frontend.external.musicbrainz_db.utils import map_deleted_mb_entities_to_unknown


def get_release_group_by_id(mbid):
    """Get release group using the MusicBrainz ID."""
    key = cache.gen_key(mbid)
    release_group = cache.get(key)
    if not release_group:
        multiple_release_groups = fetch_multiple_release_groups(
            [mbid],
            includes=['artists', 'releases', 'release-group-rels', 'url-rels', 'tags'],
        )
        if mbid in multiple_release_groups:
            release_group = multiple_release_groups.get(mbid)
        else:
            release_group = map_deleted_mb_entities_to_unknown(
                entities=multiple_release_groups,
                entity_type="release_group",
                mbids=[mbid]
            ).get(mbid)
        cache.set(key=key, val=release_group, time=DEFAULT_CACHE_EXPIRATION)
    return release_group_rel.process(release_group)


def browse_release_groups(*, artist_id, release_types=None, limit=None, offset=None):
    """Get all release groups linked to an artist.

    Args:
        artist_id (uuid): MBID of the artist.
        release_types (list): List of types of release groups to be fetched.
        limit (int): Max number of release groups to return.
        offset (int): Offset that can be used in conjunction with the limit.

    Returns:
        Tuple containing the list of dictionaries of release groups ordered by release year
        and the total count of the release groups.
    """
    artist_id = str(artist_id)
    if release_types is None:
        release_types = []
    release_types = [release_type.capitalize() for release_type in release_types]
    key = cache.gen_key(artist_id, limit, offset, *release_types)
    release_groups = cache.get(key)
    if not release_groups:
        release_groups = get_release_groups_for_artist(
            artist_id=artist_id,
            release_types=release_types,
            limit=limit,
            offset=offset
        )
        cache.set(key=key, val=release_groups, time=DEFAULT_CACHE_EXPIRATION)
    return release_groups
