from urlparse import urlparse


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
        'wikidata': {'name': 'Wikidata', 'icon': 'wikidata-16.png', },
        'discogs': {'name': 'Discogs', 'icon': 'discogs-16.png', },
        'allmusic': {'name': 'Allmusic', 'icon': 'allmusic-16.png', },
        'bandcamp': {'name': 'Bandcamp', 'icon': 'bandcamp-16.png', },
        'official homepage': {'name': 'Official homepage', 'icon': 'home-16.png', },
        'BBC Music page': {'name': 'BBC Music', },
    }
    external_urls = []
    for relation in list:
        if relation['type'] in basic_types:
            external_urls.append(dict(relation.items() + basic_types[relation['type']].items()))
        else:
            target = urlparse(relation['target'])
            if relation['type'] == 'lyrics':
                external_urls.append(dict(
                    relation.items() + {
                        'name': 'Lyrics',
                        'disambiguation': target.netloc,
                    }.items()))
            elif relation['type'] == 'wikipedia':
                external_urls.append(dict(
                    relation.items() + {
                        'name': 'Wikipedia',
                        'disambiguation': target.netloc.split('.')[0] + ':' +
                                          target.path.split('/')[2].replace("_", " "),
                        'icon': 'wikipedia-16.png',
                    }.items()))
            elif relation['type'] == 'youtube':
                external_urls.append(dict(
                    relation.items() + {
                        'name': 'YouTube',
                        'disambiguation': target.path.split('/')[2],
                        'icon': 'youtube-16.png',
                    }.items()))
            elif relation['type'] == 'social network':
                if target.netloc == 'twitter.com':
                    external_urls.append(dict(
                        relation.items() + {
                            'name': 'Twitter',
                            'disambiguation': target.path.split('/')[1],
                            'icon': 'twitter-16.png',
                        }.items()))
            else:
                # TODO: Process other types here
                pass
    external_urls.sort()
    return external_urls
