"""
Relationship processor for artist entity.
"""
import urllib.parse
from flask_babel import lazy_gettext


def process(artist):
    """Handles processing supported relation lists."""
    if 'artist-rels' in artist and artist['artist-rels']:
        artist['band-members'] = _artist(artist['artist-rels'])
    if 'url-rels' in artist and artist['url-rels']:
        artist['external-urls'] = _url(artist['url-rels'])
    return artist


def _artist(list):
    """Processor for Artist-Artist relationship.
    :returns Band members.
    """
    band_members = []
    for relation in list:
        if relation['type'] == 'member of band':
            band_members.append(relation)
    return band_members


def _url(url_list):
    """Processor for Artist-URL relationship."""
    basic_types = {
        'wikidata': {'name': lazy_gettext('Wikidata'), 'icon': 'wikidata-16.png', },
        'discogs': {'name': lazy_gettext('Discogs'), 'icon': 'discogs-16.png', },
        'allmusic': {'name': lazy_gettext('Allmusic'), 'icon': 'allmusic-16.png', },
        'bandcamp': {'name': lazy_gettext('Bandcamp'), 'icon': 'bandcamp-16.png', },
        'official homepage': {'name': lazy_gettext('Official homepage'), 'icon': 'home-16.png', },
        'BBC Music page': {'name': lazy_gettext('BBC Music'), },
    }
    external_urls = []
    for relation in url_list:
        if relation['type'] in basic_types:
            external_urls.append(dict(list(relation.items()) + list(basic_types[relation['type']].items())))
        else:
            try:
                target = urllib.parse.urlparse(relation['target'])
                if relation['type'] == 'lyrics':
                    external_urls.append(dict(
                        relation.items() + {
                            'name': lazy_gettext('Lyrics'),
                            'disambiguation': target.netloc,
                        }.items()))
                elif relation['type'] == 'wikipedia':
                    external_urls.append(dict(
                        relation.items() + {
                            'name': lazy_gettext('Wikipedia'),
                            'disambiguation': (
                                target.netloc.split('.')[0] +
                                ':' +
                                urllib.parse.unquote(target.path.split('/')[2]).decode('utf8').replace("_", " ")
                            ),
                            'icon': 'wikipedia-16.png',
                        }.items()))
                elif relation['type'] == 'youtube':
                    path = target.path.split('/')
                    if path[1] == 'user' or path[1] == 'channel':
                        disambiguation = path[2]
                    else:
                        disambiguation = path[1]
                    external_urls.append(dict(
                        relation.items() + {
                            'name': lazy_gettext('YouTube'),
                            'disambiguation': disambiguation,
                            'icon': 'youtube-16.png',
                        }.items()))
                elif relation['type'] == 'social network':
                    if target.netloc == 'twitter.com':
                        external_urls.append(dict(
                            relation.items() + {
                                'name': lazy_gettext('Twitter'),
                                'disambiguation': target.path.split('/')[1],
                                'icon': 'twitter-16.png',
                            }.items()))
                else:
                    # TODO(roman): Process other types here
                    pass
            except Exception:  # FIXME(roman): Too broad exception clause.
                # TODO(roman): Log error.
                pass

    return sorted(external_urls, key=lambda k: k['name'])
