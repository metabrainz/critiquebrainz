from musicbrainzngs import set_useragent, get_release_group_by_id, get_artist_by_id, search_release_groups, search_artists, browse_release_groups
from musicbrainzngs.musicbrainz import ResponseError

from critiquebrainz.exceptions import APIError
from critiquebrainz.cache import cache, generate_cache_key

DEFAULT_CACHE_EXPIRATION = 12 * 60 * 60  # seconds


class MusicBrainzClient:
    def init_app(self, app, app_name, app_version):
        set_useragent(app_name, app_version)
        app.jinja_env.filters['release_group_details'] = self.release_group_details

    def release_group_details(self, id):
        """Get the release group with the MusicBrainz ID."""
        key = generate_cache_key(id, type='release_group', source='api')
        details = cache.get(key)
        if not details:
            try:
                api_resp = get_release_group_by_id(id, includes=['artists']).get('release-group')
            except ResponseError as e:
                if e.cause.code == 404:
                    raise APIError(code=e.cause.code,
                                   desc="Sorry, we could not find a release group with that MusicBrainz ID.")
                else:
                    raise APIError(code=e.cause.code, desc=e.cause.msg)
            details = dict(id=api_resp.get('id'),
                           title=api_resp.get('title'),
                           artist=api_resp.get('artist-credit-phrase'),
                           artist_id=api_resp.get('artist-credit')[0].get('artist').get('id'),
                           first_release_date=api_resp.get('first-release-date')[:4])
            cache.set(key, details, DEFAULT_CACHE_EXPIRATION)
        return details

    def search_release_group(self, query='', artist='', release_group='', limit=None, offset=None):
        """Search for release groups."""
        api_resp = search_release_groups(query=query, artistname=artist, releasegroup=release_group,
                                         limit=limit, offset=offset)
        return api_resp.get('release-group-count'), api_resp.get('release-group-list')

    def search_artist(self, query='', limit=None, offset=None):
        """Search for artists."""
        api_resp = search_artists(query=query, sortname=query, alias=query, limit=limit, offset=offset)
        return api_resp.get('artist-count'), api_resp.get('artist-list')

    def artist_details(self, id):
        """Get the artist with the MusicBrainz ID."""
        key = generate_cache_key(id, type='artist', source='api')
        details = cache.get(key)
        if not details:
            try:
                details = get_artist_by_id(id).get('artist')
            except ResponseError as e:
                if e.cause.code == 404:
                    raise APIError(code=e.cause.code,
                                   desc="Sorry, we could not find an artist with that MusicBrainz ID.")
                else:
                    raise APIError(code=e.cause.code, desc=e.cause.msg)
            cache.set(key, details, DEFAULT_CACHE_EXPIRATION)
        return details

    def browse_release_groups(self, artist_id=None, release_type=[], limit=None, offset=None):
        """Get all release groups linked to an artist.
        You need to provide artist's MusicBrainz ID.
        """
        key = generate_cache_key(str(artist_id) + '_l' + str(limit) + '_of' + str(offset),
                                 type='browse_release_groups', source='api')
        release_groups = cache.get(key)
        if not release_groups:
            try:
                api_resp = browse_release_groups(artist=artist_id, release_type=release_type,
                                                 limit=limit, offset=offset)
                release_groups = api_resp.get('release-group-count'), api_resp.get('release-group-list')
            except ResponseError as e:
                raise APIError(code=e.cause.code, desc=e.cause.msg)
            cache.set(key, release_groups, DEFAULT_CACHE_EXPIRATION)
        return release_groups


musicbrainz = MusicBrainzClient()
