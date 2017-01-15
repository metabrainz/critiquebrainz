"""
This module provides access to the MusicBrainz webservice.

It uses musicbrainzngs package for making requests and parsing results.

Package musicbrainzngs is available at https://pypi.python.org/pypi/musicbrainzngs/.
More information about the MusicBrainz webservice can be found at http://wiki.musicbrainz.org/XML_Web_Service.
"""
import musicbrainzngs
from musicbrainzngs.musicbrainz import ResponseError
from brainzutils import cache
from critiquebrainz.frontend.external.relationships import artist as artist_rel
from critiquebrainz.frontend.external.relationships import release_group as release_group_rel
from werkzeug.exceptions import InternalServerError

DEFAULT_CACHE_EXPIRATION = 12 * 60 * 60  # seconds (12 hours)

THREAD_POOL_PROCESSES = 10


def init(app_name, app_version, hostname=None):
    # We need to identify our application to access the MusicBrainz webservice.
    # See https://python-musicbrainzngs.readthedocs.org/en/latest/usage/#identification for more info.
    musicbrainzngs.set_useragent(app_name, app_version)
    if hostname:
        musicbrainzngs.set_hostname(hostname)


def search_release_groups(query='', artist='', release_group='', limit=None, offset=None):
    """Search for release groups."""
    api_resp = musicbrainzngs.search_release_groups(query=query, artistname=artist, releasegroup=release_group,
                                                    limit=limit, offset=offset)
    return api_resp.get('release-group-count'), api_resp.get('release-group-list')


def search_artists(query='', limit=None, offset=None):
    """Search for artists."""
    api_resp = musicbrainzngs.search_artists(query=query, sortname=query, alias=query, limit=limit, offset=offset)
    return api_resp.get('artist-count'), api_resp.get('artist-list')


def search_events(query='', limit=None, offset=None):
    """Search for events."""
    api_resp = musicbrainzngs.search_events(query=query, limit=limit, offset=offset)
    return api_resp.get('event-count'), api_resp.get('event-list')


def search_places(query='', limit=None, offset=None):
    """Search for places."""
    api_resp = musicbrainzngs.search_places(query=query, limit=limit, offset=offset)
    return api_resp.get('place-count'), api_resp.get('place-list')


def browse_release_groups(artist_id=None, release_types=None, limit=None, offset=None):
    """Get all release groups linked to an artist.
    You need to provide artist's MusicBrainz ID.
    """
    if release_types is None:
        release_types = []
    key = cache.gen_key(artist_id, limit, offset, *release_types)
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


def browse_releases(artist_id=None, release_group=None, release_types=None, limit=None, offset=None, includes=None):
    """Get all the releases by a certain artist and/or a release group.
    You need to provide an artist's MusicBrainz ID or the Release Group's MusicBrainz ID
    """
    if release_types is None:
        release_types = []
    key = cache.gen_key(artist_id, release_group, limit, offset, *release_types, *includes)
    releases = cache.get(key)
    if not releases:
        try:
            api_resp = musicbrainzngs.browse_releases(artist=artist_id, release_type=release_types, limit=limit,
                                                      offset=offset, release_group=release_group, includes=includes)
            releases = api_resp.get('release-list')
        except ResponseError as e:
            if e.cause.code == 404:
                return None
            else:
                raise InternalServerError(e.cause.msg)
        cache.set(key=key, val=releases, time=DEFAULT_CACHE_EXPIRATION)
    return releases

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
        cache.set(key=key, val=artist, time=DEFAULT_CACHE_EXPIRATION)
    return artist_rel.process(artist)


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
                id, ['artists', 'releases', 'release-group-rels', 'url-rels', 'work-rels', 'tags']
            ).get('release-group')
        except ResponseError as e:
            if e.cause.code == 404:
                return None
            else:
                raise InternalServerError(e.cause.msg)
        cache.set(key=key, val=release_group, time=DEFAULT_CACHE_EXPIRATION)
    return release_group_rel.process(release_group)


def get_multiple_entities(entities):
    import multiprocessing.dummy as multiprocessing
    return dict(multiprocessing.Pool(THREAD_POOL_PROCESSES).map(_get_entity, entities))


def _get_entity(entity):
    return entity[0], get_entity_by_id(entity[0], type=entity[1])


def get_release_by_id(id):
    """Get release with the MusicBrainz ID.

    Returns:
        Release object with the following includes: recordings, media.
    """
    key = cache.gen_key(id)
    release = cache.get(key)
    if not release:
        try:
            release = musicbrainzngs.get_release_by_id(id, ['recordings', 'media', 'release-groups']).get('release')
        except ResponseError as e:
            if e.cause.code == 404:
                return None
            else:
                raise InternalServerError(e.cause.msg)
        cache.set(key=key, val=release, time=DEFAULT_CACHE_EXPIRATION)
    return release


def get_event_by_id(id):
    """Get event with the MusicBrainz ID.

    Returns:
        Event object with the following includes: artist-rels, place-rels, series-rels, url-rels.
    """
    key = cache.gen_key(id)
    event = cache.get(key)
    if not event:
        try:
            event = musicbrainzngs.get_event_by_id(
                id, ['artist-rels', 'place-rels', 'series-rels', 'release-group-rels', 'url-rels']).get('event')
        except ResponseError as e:
            if e.cause.code == 404:
                return None
            else:
                raise InternalServerError(e.cause.msg)
        cache.set(key=key, val=event, time=DEFAULT_CACHE_EXPIRATION)
    return event


def get_place_by_id(id):
    """Get event with the MusicBrainz ID.

    Returns:
        Event object with the following includes: artist-rels, place-rels, series-rels, url-rels.
    """
    key = cache.gen_key(id)
    place = cache.get(key)
    if not place:
        try:
            place = musicbrainzngs.get_place_by_id(
                id, ['artist-rels', 'place-rels', 'release-group-rels', 'url-rels']).get('place')
        except ResponseError as e:
            if e.cause.code == 404:
                return None
            else:
                raise InternalServerError(e.cause.msg)
        cache.set(key=key, val=place, time=DEFAULT_CACHE_EXPIRATION)
    return place


def get_entity_by_id(id, type='release_group'):
    """A wrapper to call the correct get_*_by_id function."""
    if type == 'release_group':
        rv = get_release_group_by_id(id)
    elif type == 'event':
        rv = get_event_by_id(id)
    elif type == 'place':
        rv = get_place_by_id(id)
    return rv


def get_url_rels_from_releases(releases):
    """Returns all url-rels for a list of releases in a single list (of url-rel dictionaries)
    Typical usage with browse_releases()
    """
    all_url_rels = []
    for release in releases:
        if 'url-relation-list' in release:  # Not all releases have url-rels
            all_url_rels.extend([url_rel for url_rel in release['url-relation-list']])
    return all_url_rels
