from critiquebrainz.frontend.external import musicbrainz
from urllib.parse import urlencode
import re


def get_url(mbid):
    all_url_rels = musicbrainz.get_url_rels_from_releases(musicbrainz.browse_releases(release_group=mbid,
                                                                                      includes=['url-rels']))
    for url_rel in all_url_rels:
        if url_rel['type-id'] == '08445ccf-7b99-4438-9f9a-fb9ac18099ee':  # Type-id for streaming music
            if re.match(r'^(http|https)://soundcloud.com', url_rel['target']):
                return urlencode(url_rel['target'])
    return None
