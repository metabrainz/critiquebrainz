import musicbrainzngs
from musicbrainzngs.musicbrainz import ResponseError

import critiquebrainz
from critiquebrainz.cache import cache, generate_cache_key
from critiquebrainz.frontend.apis.exceptions import APIError
from relationships import artist as artist_rel, release_group as release_group_rel

from multiprocessing import Pool


DEFAULT_CACHE_EXPIRATION = 12 * 60 * 60  # seconds

musicbrainzngs.set_useragent("CritiqueBrainz Client", critiquebrainz.__version__)


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
    key = generate_cache_key(str(artist_id), type='browse_release_groups', source='api',
                             params=[limit, offset] + release_types)
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
                raise APIError(code=e.cause.code, desc=e.cause.msg)
        cache.set(key, release_groups, DEFAULT_CACHE_EXPIRATION)
    return release_groups


def get_artist_by_id(id, includes=None):
    """Get artist with the MusicBrainz ID.
    Available includes: recordings, releases, release-groups, works, various-artists, discids, media, isrcs,
    aliases, annotation, tags, user-tags, ratings, user-ratings, area-rels, artist-rels, label-rels, place-rels,
    recording-rels, release-rels, release-group-rels, url-rels, work-rels.
    """
    if includes is None:
        includes = []
    key = generate_cache_key(id, type='artist', source='api', params=includes)
    artist = cache.get(key)
    if not artist:
        try:
            artist = musicbrainzngs.get_artist_by_id(id, includes).get('artist')
        except ResponseError as e:
            if e.cause.code == 404:
                return None
            else:
                raise APIError(code=e.cause.code, desc=e.cause.msg)
        artist = artist_rel.process(artist)
        cache.set(key, artist, DEFAULT_CACHE_EXPIRATION)
    return artist


def get_release_group_by_id(id, includes=None):
    """Get release group with the MusicBrainz ID.
    Available includes: artists, releases, discids, media, artist-credits, annotation, aliases, tags, user-tags,
    ratings, user-ratings, area-rels, artist-rels, label-rels, place-rels, recording-rels, release-rels,
    release-group-rels, url-rels, work-rels.
    """
    if includes is None:
        includes = []
    key = generate_cache_key(id, type='release_group', source='api', params=includes)
    release_group = cache.get(key)
    if not release_group:
        try:
            release_group = musicbrainzngs.get_release_group_by_id(id, includes).get('release-group')
        except ResponseError as e:
            if e.cause.code == 404:
                return None
            else:
                raise APIError(code=e.cause.code, desc=e.cause.msg)
        release_group = release_group_rel.process(release_group)
        cache.set(key, release_group, DEFAULT_CACHE_EXPIRATION)
    return release_group


def get_release_by_id(id, includes=None):
    """Get release with the MusicBrainz ID.
    Available includes: artists, labels, recordings, release-groups, media, artist-credits, discids, isrcs,
    recording-level-rels, work-level-rels, annotation, aliases, area-rels, artist-rels, label-rels, place-rels,
    recording-rels, release-rels, release-group-rels, url-rels, work-rels.
    """
    if includes is None:
        includes = []
    key = generate_cache_key(id, type='release', source='api', params=includes)
    release = cache.get(key)
    if not release:
        try:
            release = musicbrainzngs.get_release_by_id(id, includes).get('release')
        except ResponseError as e:
            if e.cause.code == 404:
                return None
            else:
                raise APIError(code=e.cause.code, desc=e.cause.msg)
        cache.set(key, release, DEFAULT_CACHE_EXPIRATION)
    return release


def release_group_details(mbid):
    return get_release_group_by_id(mbid, includes=['artists'])


def get_multiple_release_groups(mbids):
    pool = Pool(processes=10)
    return dict(pool.map(_get_rg, mbids))


def _get_rg(mbid):
    return mbid, release_group_details(mbid)
