from critiquebrainz.frontend.external import musicbrainz
from urllib.parse import urlencode


def mapping(mbid):
    release_group = musicbrainz.get_release_group_by_id(mbid)
    if 'url-relation-list' in release_group and release_group['url-relation-list']:
        for relation in release_group['url-relation-list']:
            url = relation['target']
            if 'soundcloud.com' in url:
                return urlencode(url)

    return None

