"""
Relationship processor for release group entity.
"""
import urllib.parse
from flask_babel import lazy_gettext


def process(release_group):
    """Handles processing supported relation lists."""
    if 'url-rels' in release_group and release_group['url-rels']:
        release_group['external-urls'] = _url(release_group['url-rels'])
    return release_group


def _url(url_list):
    """Processor for Release Group-URL relationship."""
    basic_types = {
        'wikidata': {'name': lazy_gettext('Wikidata'), 'icon': 'wikidata-16.png', },
        'discogs': {'name': lazy_gettext('Discogs'), 'icon': 'discogs-16.png', },
        'allmusic': {'name': lazy_gettext('Allmusic'), 'icon': 'allmusic-16.png', },
        'official homepage': {'name': lazy_gettext('Official homepage'), 'icon': 'home-16.png', },
        'recording studio': {'name': lazy_gettext('Recording studio'), },
    }
    external_urls = []
    for relation in url_list:
        if relation['type'] in basic_types:
            external_urls.append(dict(list(relation.items()) + list(basic_types[relation['type']].items())))
        else:
            try:
                target = urllib.parse.urlparse(relation['url']['url'])
                if relation['type'] == 'lyrics':
                    external_urls.append(dict(
                        relation.items() + {
                            'name': lazy_gettext('Lyrics'),
                            'disambiguation': target.netloc
                        }.items()))
                elif relation['type'] == 'wikipedia':
                    external_urls.append(dict(
                        relation.items() + {
                            'name': lazy_gettext('Wikipedia'),
                            'disambiguation': (
                                target.netloc.split('.')[0] +
                                ':' +
                                urllib.parse.unquote(target.path.split('/')[2]).decode('utf8').replace("_", " "),
                            ),
                            'icon': 'wikipedia-16.png',
                        }.items()))
                else:
                    # TODO(roman): Process other types here
                    pass
            except Exception:  # FIXME(roman): Too broad exception clause.
                # TODO(roman): Log error.
                pass

    return sorted(external_urls, key=lambda k: k['name'])
