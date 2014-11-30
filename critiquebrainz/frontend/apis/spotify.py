"""
This module provides functions that can help access Spotify Web API.

More information about it is available at https://developer.spotify.com/web-api/.
"""
import requests
import urllib
from critiquebrainz import cache

DEFAULT_CACHE_EXPIRATION = 12 * 60 * 60  # seconds (12 hours)

BASE_URL = "https://api.spotify.com/v1"


def search(query, type, limit=20, offset=0):
    """Get Spotify catalog information about artists, albums, or tracks that
    match a keyword string.

    More information is available at https://developer.spotify.com/web-api/search-item/.
    """
    key = cache.prep_cache_key(query, [type, limit, offset])
    key_prefix = "spotify_search"
    result = cache.get(key, key_prefix)
    if not result:
        result = requests.get("%s/search?q=%s&type=%s&limit=%s&offset=%s" %
                              (BASE_URL, urllib.quote(query.encode('utf8')),
                               type, str(limit), str(offset))).json()
        cache.set(key=key, key_prefix=key_prefix, val=result,
                  time=DEFAULT_CACHE_EXPIRATION)
    return result


def get_album(spotify_id):
    """Get Spotify catalog information for a single album.

    Returns:
        Album object from Spotify. More info about this type of object is
        available at https://developer.spotify.com/web-api/object-model/#album-object.
    """
    key_prefix = "spotify_album"
    album = cache.get(spotify_id, key_prefix)
    if not album:
        album = requests.get("%s/albums/%s" % (BASE_URL, spotify_id)).json()
        cache.set(key=spotify_id, key_prefix=key_prefix, val=album,
                  time=DEFAULT_CACHE_EXPIRATION)
    return album


def get_multiple_albums(spotify_ids):
    """Get Spotify catalog information for multiple albums identified by their
    Spotify IDs.

    Returns:
        List of album objects from Spotify. More info about this type of objects
        is available at https://developer.spotify.com/web-api/object-model/#album-object.
    """
    key_prefix = "spotify_album"
    albums = cache.get_multi(spotify_ids, key_prefix)

    # Checking which albums weren't in cache
    for album_id in albums.keys():
        if album_id in spotify_ids:
            spotify_ids.remove(album_id)

    if len(spotify_ids) > 0:
        resp = requests.get("%s/albums?ids=%s" % (BASE_URL, ','.join(spotify_ids))).json()['albums']

        received_albums = {}
        for album in resp:
            received_albums[album['id']] = album

        cache.set_multi(received_albums, key_prefix=key_prefix, time=DEFAULT_CACHE_EXPIRATION)

        albums = dict(albums.items() + received_albums.items())

    return albums
