from musicbrainzngs import set_useragent, get_release_group_by_id, get_artist_by_id, search_release_groups, search_artists, browse_release_groups
from musicbrainzngs.musicbrainz import ResponseError

from critiquebrainz.exceptions import APIError


class MusicBrainzClient:
    def init_app(self, app, app_name, app_version):
        set_useragent(app_name, app_version)
        app.jinja_env.filters['album_details'] = self.album_details

    def album_details(self, release_group):
        try:
            api_resp = get_release_group_by_id(release_group, includes=['artists']).get('release-group')
        except ResponseError as e:
            if e.cause.code == 404:
                raise APIError(code=e.cause.code,
                               desc="Sorry, we could not find a release group with that MusicBrainz ID.")
            else:
                raise APIError(code=e.cause.code, desc=e.cause.msg)
        resp = dict(title=api_resp.get('title'),
                    artist=api_resp.get('artist-credit-phrase'),
                    artist_id=api_resp.get('artist-credit')[0].get('artist').get('id'),
                    release_date=api_resp.get('first-release-date')[:4])
        return resp

    def search_release_group(self, query='', artist='', album='', limit=None, offset=None):
        api_resp = search_release_groups(query=query, artistname=artist, releasegroup=album, limit=limit, offset=offset)
        return api_resp.get('release-group-list')

    def search_artist(self, query='', limit=None, offset=None):
        api_resp = search_artists(query=query, sortname=query, alias=query, limit=limit, offset=offset)
        return api_resp.get('artist-list')

    def artist_details(self, id):
        try:
            api_resp = get_artist_by_id(id).get('artist')
        except ResponseError as e:
            if e.cause.code == 404:
                raise APIError(code=e.cause.code,
                               desc="Sorry, we could not find an artist with that MusicBrainz ID.")
            else:
                raise APIError(code=e.cause.code, desc=e.cause.msg)
        resp = dict(name=api_resp.get('name'),
                    type=api_resp.get('type'))
        return resp

    def browse_release_groups(self, artist=None, release=None, limit=None, offset=None):
        try:
            api_resp = browse_release_groups(artist=artist, release=release, limit=limit, offset=offset)
        except ResponseError as e:
            raise APIError(code=e.cause.code, desc=e.cause.msg)
        return api_resp.get('release-group-count'), api_resp.get('release-group-list')


musicbrainz = MusicBrainzClient()
