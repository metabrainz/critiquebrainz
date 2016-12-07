from critiquebrainz.frontend.external import musicbrainz
import re
import requests
import yaml


def get_url(mbid):
    all_url_rels = musicbrainz.get_url_rels_from_releases(musicbrainz.browse_releases(release_group=mbid,
                                                                                      includes=['url-rels']))
    streaming_url_rels = {'soundcloud': None, 'bandcamp': None}
    for url_rel in all_url_rels:
        if url_rel['type-id'] == '08445ccf-7b99-4438-9f9a-fb9ac18099ee':  # Type-id for streaming music
            if re.match(r'^(http|https)://soundcloud.com', url_rel['target']):
                streaming_url_rels['soundcloud'] = url_rel['target']
            elif re.match(r'^(http|https)://[A-Za-z0-9]+.bandcamp.com/?', url_rel['target']):
                streaming_url_rels['bandcamp'] = bandcamp_parser(url_rel['target'])
    return streaming_url_rels


def bandcamp_parser(bandcamp_link):
    """Gives the unique bandcamp id of the entered album/release
    Required for embedding the player.
    """
    html = requests.get(bandcamp_link).text
    html = html[html.find('{', html.find('EmbedData')):html.find('};', html.find('{', html.find('EmbedData'))) + 1].strip()
    html = html[html.find('{', html.find('tralbum_param')):html.find('}', html.find('{', html.find('tralbum_param'))) + 1]
    embed_data = yaml.load(html)
    mapping = '{}={}'.format(embed_data['name'], embed_data['value'])
    return mapping
