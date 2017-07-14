"""
This module provides access to Spotify Web API.

More information about it is available at https://developer.spotify.com/web-api/.
"""
from base64 import b64encode
import urllib.parse
import requests
from brainzutils import cache
from flask import current_app as app
from critiquebrainz.frontend.external.exceptions import ExternalServiceException

DEFAULT_CACHE_EXPIRATION = 12 * 60 * 60  # seconds (12 hours)
ACCESS_TOKEN_EXPIRATION = 60 * 60 # seconds (1 hour)

BASE_URL = "https://api.spotify.com/v1"


def _fetch_access_token():
    """Get an access token from the oauth credentials."""

    key = cache.gen_key("spotify_access_token")
    namespace = "spotify_access_token"
    access_token = cache.get(key, namespace)

    client_id = app.config.get("SPOTIFY_CLIENT_ID")
    client_secret = app.config.get("SPOTIFY_CLIENT_SECRET")
    auth_value = b64encode(bytes(f"{client_id}:{client_secret}", "utf-8")).decode("utf-8")

    if not access_token:
        access_token = requests.post(
            "https://accounts.spotify.com/api/token",
            data={"grant_type": "client_credentials"},
            headers={"Authorization": f"Basic {auth_value}"},
        ).json()
        access_token = access_token.get('access_token')
        if not access_token:
            raise SpotifyWebAPIException("Could not fetch access token for Spotify API")
        cache.set(key=key, namespace=namespace, val=access_token, time=ACCESS_TOKEN_EXPIRATION)
    return access_token


def _get_spotify(query):
    """Make a GET request to Spotify Web API.

    Args:
        query (str): Query to the Web API.

    Returns:
        Dictionary containing the information.
    """
    access_token = _fetch_access_token()
    url = BASE_URL + query
    headers = {"Authorization": f"Bearer {access_token}"}

    result = requests.get(f"{url}", headers=headers)
    return result.json()


def search(query, type, limit=20, offset=0):
    """Get Spotify catalog information about artists, albums, or tracks that
    match a keyword string.

    More information is available at https://developer.spotify.com/web-api/search-item/.
    """
    key = cache.gen_key(query, type, limit, offset)
    namespace = "spotify_search"
    result = cache.get(key, namespace)
    if not result:
        result = _get_spotify("/search?q=%s&type=%s&limit=%s&offset=%s" %
                              (urllib.parse.quote(query.encode('utf8')), type, str(limit), str(offset)))
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
        album = _get_spotify("/albums/%s" % (spotify_id))
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

    if spotify_ids:
        resp = _get_spotify("/albums?ids=%s" % (','.join(spotify_ids)))["albums"]

        received_albums = {}
        for album in resp:
            if album is not None:
                received_albums[album['id']] = album

        cache.set_many(received_albums, namespace=namespace, time=DEFAULT_CACHE_EXPIRATION)

        albums.update(received_albums)

    return albums


class SpotifyException(ExternalServiceException):
    """Exception related to errors related to the Spotify API."""
    pass
