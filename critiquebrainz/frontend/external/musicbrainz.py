"""
This module provides access to the MusicBrainz webservice.

It uses musicbrainzngs package for making requests and parsing results.

Package musicbrainzngs is available at https://pypi.python.org/pypi/musicbrainzngs/.
More information about the MusicBrainz webservice can be found at http://wiki.musicbrainz.org/XML_Web_Service.
"""
import musicbrainzngs


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


def search_labels(query='', limit=None, offset=None):
    """Search for labels."""
    api_resp = musicbrainzngs.search_labels(query=query, limit=limit, offset=offset)
    return api_resp.get('label-count'), api_resp.get('label-list')
