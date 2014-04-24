from musicbrainzngs import set_useragent, get_release_group_by_id, search_release_groups
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
                    release_date=api_resp.get('first-release-date')[:4])
        return resp

    def search_release_group(self, artist, album, limit, offset):
        api_resp = search_release_groups(album, limit, offset, artistname=artist)
        return api_resp.get('release-group-list')


musicbrainz = MusicBrainzClient()
