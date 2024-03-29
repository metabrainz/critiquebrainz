"""
This module provides access to Spotify Web API.

More information about it is available at https://developer.spotify.com/web-api/.
"""
import logging
import urllib.parse
from base64 import b64encode
from http import HTTPStatus
from typing import List

import requests
from brainzutils import cache
from flask import current_app as app

from critiquebrainz.frontend.external.exceptions import ExternalServiceException

_DEFAULT_CACHE_EXPIRATION = 12 * 60 * 60  # seconds (12 hours)
_BASE_URL = "https://api.spotify.com/v1/"


def search(query: str, *, item_types="", limit=20, offset=0) -> dict:
    """Search for items (artists, albums, or tracks) by a query string.

    More information is available at https://developer.spotify.com/web-api/search-item/.
    """
    cache_key = cache.gen_key(query, item_types, limit, offset)
    cache_namespace = "spotify_search"
    result = cache.get(cache_key, cache_namespace)
    if not result:
        query = urllib.parse.quote(query.encode('utf8'))
        result = _get(f"search?q={query}&type={item_types}&limit={str(limit)}&offset={str(offset)}")
        cache.set(cache_key, result, _DEFAULT_CACHE_EXPIRATION, namespace=cache_namespace)
    return result


def get_album(spotify_id: str) -> dict:
    """Get information about an album.

    Args:
        spotify_id: Spotify ID of an album.

    Returns:
        Album object from Spotify. More info about this type of object is
        available at https://developer.spotify.com/web-api/object-model/#album-object.
    """
    cache_namespace = "spotify_album"
    album = cache.get(spotify_id, cache_namespace)
    if not album:
        album = _get(f"albums/{spotify_id}")
        cache.set(spotify_id, album, _DEFAULT_CACHE_EXPIRATION, namespace=cache_namespace)
    return album


def get_multiple_albums(spotify_ids: List[str]) -> dict:
    """Get information about multiple albums.

    Args:
        spotify_ids: List of Spotify IDs of albums.

    Returns:
        Dict of album objects from Spotify. More info about this type of objects
        is available at https://developer.spotify.com/web-api/object-model/#album-object.
    """
    if not spotify_ids:
        return {}
    spotify_ids = list(spotify_ids)
    cache_namespace = "spotify_albums"
    albums = cache.get_many(spotify_ids, cache_namespace)

    # fetch album for only those ids that are not in cache
    for album_id, data in albums.items():
        if data is not None and album_id in spotify_ids:
            spotify_ids.remove(album_id)

    if spotify_ids:
        response = _get(f"albums?ids={','.join(spotify_ids)}")
        if "albums" not in response:
            logging.error("Album data is missing from a Spotify response", extra={
                "spotify_ids": spotify_ids,
                "response": response,
            })
            raise SpotifyUnexpectedResponseException("Album data is missing")

        received_albums = {}
        for album in response["albums"]:
            if album is not None:
                received_albums[album['id']] = album
        cache.set_many(received_albums, _DEFAULT_CACHE_EXPIRATION, namespace=cache_namespace)
        albums.update(received_albums)
    return albums


def _get(query: str) -> dict:
    """Make a GET request to the Spotify Web API.

    This function adds appropriate authorization header to make sure that
    request goes through. Gets a fresh access token if expired.

    Args:
        query (str): Query string that would be added to the base URL.
                     Shouldn't start with a slash.

    Returns:
        Parsed JSON response as a dictionary containing the information.
    """
    RETRY_COUNTS = 5
    refresh = False
    for _ in range(RETRY_COUNTS):
        response = requests.get(_BASE_URL + query, headers={
            "Authorization": f"Bearer {_fetch_access_token(refresh=refresh)}"
        })
        if response.status_code != HTTPStatus.OK:
            refresh = response.status_code == HTTPStatus.UNAUTHORIZED
        else:
            break
    else:
        app.logger.error("Unexpected response from the Spotify API", extra={
            "query": query,
            "response": response.__getstate__(),
        })
        raise SpotifyUnexpectedResponseException("Unexpected response from the Spotify API")
    return response.json()


def _fetch_access_token(refresh=False) -> str:
    """Get an access token from the OAuth credentials.

    https://developer.spotify.com/web-api/authorization-guide/#client-credentials-flow
    """
    key = cache.gen_key("spotify_oauth_access_token")
    access_token = cache.get(key)
    if refresh or not access_token:
        client_id = app.config.get("SPOTIFY_CLIENT_ID")
        client_secret = app.config.get("SPOTIFY_CLIENT_SECRET")
        auth_value = b64encode(bytes(f"{client_id}:{client_secret}", "utf-8")).decode("utf-8")
        response = requests.post(
            "https://accounts.spotify.com/api/token",
            data={"grant_type": "client_credentials"},
            headers={"Authorization": f"Basic {auth_value}"},
        ).json()
        access_token = response.get("access_token")
        if not access_token:
            raise SpotifyException("Could not fetch access token for Spotify API")
        # Making the token stored in cache expire at the same time as the actual token
        cache.set(key=key, val=access_token, expirein=response.get("expires_in", 10))
    return access_token


class SpotifyException(ExternalServiceException):
    """Exception related to errors related to the Spotify API."""


class SpotifyUnexpectedResponseException(SpotifyException):
    pass
