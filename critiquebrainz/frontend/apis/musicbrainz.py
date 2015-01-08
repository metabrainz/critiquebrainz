"""
This module simplifies access to the MusicBrainz webservice. It uses musicbrainzngs package.

Package musicbrainzngs is available at https://pypi.python.org/pypi/musicbrainzngs/.
More information about the MusicBrainz webservice can be found at http://wiki.musicbrainz.org/XML_Web_Service.
"""
import musicbrainzngs
from musicbrainzngs.musicbrainz import ResponseError
from critiquebrainz import cache
from critiquebrainz.frontend.apis.relationships import artist as artist_rel
from critiquebrainz.frontend.apis.relationships import release_group as release_group_rel
from werkzeug.exceptions import InternalServerError

DEFAULT_CACHE_EXPIRATION = 12 * 60 * 60  # seconds (12 hours)

THREAD_POOL_PROCESSES = 10


def init(app_name, app_version):
    # We need to identify our application to access the MusicBrainz webservice.
    # See https://python-musicbrainzngs.readthedocs.org/en/latest/usage/#identification for more info.
    musicbrainzngs.set_useragent(app_name, app_version)


def search_release_groups(query='', artist='', release_group='', limit=None, offset=None):
    """Search for release groups."""
    api_resp = musicbrainzngs.search_release_groups(query=query, artistname=artist, releasegroup=release_group,
                                                    limit=limit, offset=offset)
    return api_resp.get('release-group-count'), api_resp.get('release-group-list')


def search_artists(query='', limit=None, offset=None):
    """Search for artists."""
    api_resp = musicbrainzngs.search_artists(query=query, sortname=query, alias=query, limit=limit, offset=offset)
    return api_resp.get('artist-count'), api_resp.get('artist-list')


def browse_release_groups(artist_id=None, release_types=None, limit=None, offset=None):
    """Get all release groups linked to an artist.
    You need to provide artist's MusicBrainz ID.
    """
    if release_types is None:
        release_types = []
    key = cache.gen_key(artist_id, [limit, offset] + release_types)
    release_groups = cache.get(key)
    if not release_groups:
        try:
            api_resp = musicbrainzngs.browse_release_groups(artist=artist_id, release_type=release_types,
                                                            limit=limit, offset=offset)
            release_groups = api_resp.get('release-group-count'), api_resp.get('release-group-list')
        except ResponseError as e:
            if e.cause.code == 404:
                return None
            else:
                raise InternalServerError(e.cause.msg)
        cache.set(key=key, val=release_groups, time=DEFAULT_CACHE_EXPIRATION)
    return release_groups


def get_artist_by_id(id):
    """Get artist with the MusicBrainz ID.

    Returns:
        Artist object with the following includes: url-rels, artist-rels.
    """
    key = cache.gen_key(id)
    artist = cache.get(key)
    if not artist:
        try:
            artist = musicbrainzngs.get_artist_by_id(id, ['url-rels', 'artist-rels']).get('artist')
        except ResponseError as e:
            if e.cause.code == 404:
                return None
            else:
                raise InternalServerError(e.cause.msg)
        artist = artist_rel.process(artist)
        cache.set(key=key, val=artist, time=DEFAULT_CACHE_EXPIRATION)
    return artist


def get_release_group_by_id(id):
    """Get release group with the MusicBrainz ID.

    Returns:
        Release group object with the following includes: artists, releases,
        release-group-rels, url-rels, work-rels.
    """
    key = cache.gen_key(id)
    release_group = cache.get(key)
    if not release_group:
        try:
            release_group = musicbrainzngs.get_release_group_by_id(
                id, ['artists', 'releases', 'release-group-rels', 'url-rels', 'work-rels']
            ).get('release-group')
        except ResponseError as e:
            if e.cause.code == 404:
                return None
            else:
                raise InternalServerError(e.cause.msg)
        release_group = release_group_rel.process(release_group)
        cache.set(key=key, val=release_group, time=DEFAULT_CACHE_EXPIRATION)
    return release_group


def get_multiple_release_groups(mbids):
    import multiprocessing.dummy as multiprocessing
    return dict(multiprocessing.Pool(THREAD_POOL_PROCESSES).map(_get_rg, mbids))


def _get_rg(mbid):
    return mbid, get_release_group_by_id(mbid)


def get_release_by_id(id):
    """Get release with the MusicBrainz ID.

    Returns:
        Release object with the following includes: recordings, media.
    """
    key = cache.gen_key(id)
    release = cache.get(key)
    if not release:
        try:
            release = musicbrainzngs.get_release_by_id(id, ['recordings', 'media']).get('release')
        except ResponseError as e:
            if e.cause.code == 404:
                return None
            else:
                raise InternalServerError(e.cause.msg)
        cache.set(key=key, val=release, time=DEFAULT_CACHE_EXPIRATION)
    return release
