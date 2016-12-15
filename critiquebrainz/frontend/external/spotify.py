"""
This module provides access to Spotify Web API.

More information about it is available at https://developer.spotify.com/web-api/.
"""
import requests
import urllib.parse
from brainzutils import cache

DEFAULT_CACHE_EXPIRATION = 12 * 60 * 60  # seconds (12 hours)

BASE_URL = "https://api.spotify.com/v1"


def search(query, type, limit=20, offset=0):
    """Get Spotify catalog information about artists, albums, or tracks that
    match a keyword string.

    More information is available at https://developer.spotify.com/web-api/search-item/.
    """
    key = cache.gen_key(query, type, limit, offset)
    namespace = "spotify_search"
    result = cache.get(key, namespace)
    if not result:
        result = requests.get("%s/search?q=%s&type=%s&limit=%s&offset=%s" %
                              (BASE_URL, urllib.parse.quote(query.encode('utf8')),
                               type, str(limit), str(offset))).json()
        cache.set(key=key, namespace=namespace, val=result,
                  time=DEFAULT_CACHE_EXPIRATION)
    return result


def get_album(spotify_id):
    """Get Spotify catalog information for a single album.

    Returns:
        Album object from Spotify. More info about this type of object is
        available at https://developer.spotify.com/web-api/object-model/#album-object.
    """
    namespace = "spotify_album"
    album = cache.get(spotify_id, namespace)
    if not album:
        album = requests.get("%s/albums/%s" % (BASE_URL, spotify_id)).json()
        cache.set(key=spotify_id, namespace=namespace, val=album,
                  time=DEFAULT_CACHE_EXPIRATION)
    return album


def get_multiple_albums(spotify_ids):
    """Get Spotify catalog information for multiple albums identified by their
    Spotify IDs.

    Returns:
        List of album objects from Spotify. More info about this type of objects
        is available at https://developer.spotify.com/web-api/object-model/#album-object.
    """
    namespace = "spotify_albums"
    albums = cache.get_many(spotify_ids, namespace)

    # Checking which albums weren't in cache
    for album_id, data in albums.items():
        if data is not None and album_id in spotify_ids:
            spotify_ids.remove(album_id)

    if len(spotify_ids) > 0:
        resp = requests.get("%s/albums?ids=%s" % (BASE_URL, ','.join(spotify_ids))).json()['albums']

        received_albums = {}
        for album in resp:
            if album is not None:
                received_albums[album['id']] = album

        cache.set_many(received_albums, namespace=namespace, time=DEFAULT_CACHE_EXPIRATION)

        albums.update(received_albums)

    return albums
