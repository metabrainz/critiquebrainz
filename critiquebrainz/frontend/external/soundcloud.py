import re
import critiquebrainz.frontend.external.musicbrainz_db.release as mb_release


def get_url(mbid):
    all_url_rels = mb_release.get_url_rels_from_releases(
        mb_release.browse_releases(release_group_id=mbid, includes=['url-rels']) or {}
    )
    for url_rel in all_url_rels:
        if url_rel['type-id'] == '08445ccf-7b99-4438-9f9a-fb9ac18099ee':  # "streaming music"
            if re.match(r'^(http|https)://soundcloud.com', url_rel['url']['url']):
                return url_rel['url']['url']
    return None
