import requests
import urllib
from critiquebrainz.cache import cache, generate_cache_key

DEFAULT_CACHE_EXPIRATION = 12 * 60 * 60  # seconds


class SpotifyClient(object):
    """Provides interface to Spotify Web API."""

    BASE_URL = "https://api.spotify.com/v1/"

    def search(self, query, type, limit=20, offset=0):
        """Get Spotify catalog information about artists, albums, or tracks that match a keyword string."""
        key = generate_cache_key('search', source='spotify', params=[query, type, limit, offset])
        resp = cache.get(key)
        if not resp:
            resp = requests.get(self.BASE_URL +
                                'search?q=' + urllib.quote(query.encode('utf8')) +
                                '&type=' + type +
                                '&limit=' + str(limit) +
                                '&offset=' + str(offset)).json()
            cache.set(key, resp, DEFAULT_CACHE_EXPIRATION)
        return resp
