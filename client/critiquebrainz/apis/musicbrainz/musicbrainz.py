from musicbrainzngs import set_useragent, get_release_group_by_id, get_artist_by_id, search_release_groups, search_artists, browse_release_groups
from musicbrainzngs.musicbrainz import ResponseError

from critiquebrainz.exceptions import APIError
from critiquebrainz.cache import cache, generate_cache_key
from relationships import artist as artist_rel, release_group as release_group_rel

DEFAULT_CACHE_EXPIRATION = 12 * 60 * 60  # seconds


class MusicBrainzClient:
    """Provides an interface to MusicBrainz data."""

    def init_app(self, app, app_name, app_version):
        set_useragent(app_name, app_version)
        app.jinja_env.filters['release_group_details'] = self.release_group_details

    def search_release_groups(self, query='', artist='', release_group='', limit=None, offset=None):
        """Search for release groups."""
        api_resp = search_release_groups(query=query, artistname=artist, releasegroup=release_group,
                                         limit=limit, offset=offset)
        return api_resp.get('release-group-count'), api_resp.get('release-group-list')

    def search_artists(self, query='', limit=None, offset=None):
        """Search for artists."""
        api_resp = search_artists(query=query, sortname=query, alias=query, limit=limit, offset=offset)
        return api_resp.get('artist-count'), api_resp.get('artist-list')

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

    def get_artist_by_id(self, id, includes=[]):
        """Get artist with the MusicBrainz ID.
        Available includes: recordings, releases, release-groups, works, various-artists, discids, media, isrcs,
        aliases, annotation, tags, user-tags, ratings, user-ratings, area-rels, artist-rels, label-rels, place-rels,
        recording-rels, release-rels, release-group-rels, url-rels, work-rels.
        """
        try:
            artist = get_artist_by_id(id, includes).get('artist')
        except ResponseError as e:
            if e.cause.code == 404:
                raise APIError(code=e.cause.code,
                               desc="Sorry, we could not find an artist with that MusicBrainz ID.")
            else:
                raise APIError(code=e.cause.code, desc=e.cause.msg)
        artist = artist_rel.process(artist)
        return artist

    def get_release_group_by_id(self, id, includes=[]):
        """Get release group with the MusicBrainz ID.
        Available includes: artists, releases, discids, media, artist-credits, annotation, aliases, tags, user-tags,
        ratings, user-ratings, area-rels, artist-rels, label-rels, place-rels, recording-rels, release-rels,
        release-group-rels, url-rels, work-rels.
        """
        try:
            release_group = get_release_group_by_id(id, includes).get('release-group')
        except ResponseError as e:
            if e.cause.code == 404:
                raise APIError(code=e.cause.code,
                               desc="Sorry, we could not find a release group with that MusicBrainz ID.")
            else:
                raise APIError(code=e.cause.code, desc=e.cause.msg)
        release_group = release_group_rel.process(release_group)
        return release_group

    def release_group_details(self, id):
        """Get short release group details.
        :returns Dictionary with an ID, title, artist and artist ID, first release year.
        """
        key = generate_cache_key(id, type='release_group', source='api')
        details = cache.get(key)
        if not details:
            api_resp = self.get_release_group_by_id(id, includes=['artists'])
            details = dict(id=api_resp.get('id'),
                           title=api_resp.get('title'),
                           artist=api_resp.get('artist-credit-phrase'),
                           artist_id=api_resp.get('artist-credit')[0].get('artist').get('id'),
                           first_release_date=api_resp.get('first-release-date')[:4])
            cache.set(key, details, DEFAULT_CACHE_EXPIRATION)
        return details
