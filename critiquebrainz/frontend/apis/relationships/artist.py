"""
Relationship processor for artist entity.
"""
from urlparse import urlparse
from flask_babel import gettext
import urllib


def process(artist):
    """Handles processing supported relation lists."""
    if 'artist-relation-list' in artist and artist['artist-relation-list']:
        artist['band-members'] = _artist(artist['artist-relation-list'])
    if 'url-relation-list' in artist and artist['url-relation-list']:
        artist['external-urls'] = _url(artist['url-relation-list'])
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


def _url(list):
    """Processor for Artist-URL relationship."""
    basic_types = {
        'wikidata': {'name': gettext('Wikidata'), 'icon': 'wikidata-16.png', },
        'discogs': {'name': gettext('Discogs'), 'icon': 'discogs-16.png', },
        'allmusic': {'name': gettext('Allmusic'), 'icon': 'allmusic-16.png', },
        'bandcamp': {'name': gettext('Bandcamp'), 'icon': 'bandcamp-16.png', },
        'official homepage': {'name': gettext('Official homepage'), 'icon': 'home-16.png', },
        'BBC Music page': {'name': gettext('BBC Music'), },
    }
    external_urls = []
    for relation in list:
        if relation['type'] in basic_types:
            external_urls.append(dict(relation.items() + basic_types[relation['type']].items()))
        else:
            try:
                target = urlparse(relation['target'])
                if relation['type'] == 'lyrics':
                    external_urls.append(dict(
                        relation.items() + {
                            'name': gettext('Lyrics'),
                            'disambiguation': target.netloc,
                        }.items()))
                elif relation['type'] == 'wikipedia':
                    external_urls.append(dict(
                        relation.items() + {
                            'name': gettext('Wikipedia'),
                            'disambiguation': target.netloc.split('.')[0] + ':' +
                                              urllib.unquote(target.path.split('/')[2]).decode('utf8').replace("_", " "),
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
                            'name': gettext('YouTube'),
                            'disambiguation': disambiguation,
                            'icon': 'youtube-16.png',
                        }.items()))
                elif relation['type'] == 'social network':
                    if target.netloc == 'twitter.com':
                        external_urls.append(dict(
                            relation.items() + {
                                'name': gettext('Twitter'),
                                'disambiguation': target.path.split('/')[1],
                                'icon': 'twitter-16.png',
                            }.items()))
                else:
                    # TODO(roman): Process other types here
                    pass
            except Exception as e:  # FIXME(roman): Too broad exception clause.
                # TODO(roman): Log error.
                pass
    external_urls.sort()
    return external_urls
