from urlparse import urlparse


def process(release_group):
    """Handles processing supported relation lists."""
    if 'url-relation-list' in release_group and release_group['url-relation-list']:
        release_group['external-urls'] = _url(release_group['url-relation-list'])
    return release_group


def _url(list):
    """Processor for Release Group-URL relationship."""
    basic_types = {
        'wikidata': {'name': 'Wikidata', 'icon': 'wikidata-16.png', },
        'discogs': {'name': 'Discogs', 'icon': 'discogs-16.png', },
        'allmusic': {'name': 'Allmusic', 'icon': 'allmusic-16.png', },
        'official homepage': {'name': 'Official homepage', 'icon': 'home-16.png', },
        'recording studio': {'name': 'Recording studio', },
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
                            'name': 'Lyrics',
                            'disambiguation': target.netloc
                        }.items()))
                elif relation['type'] == 'wikipedia':
                    external_urls.append(dict(
                        relation.items() + {
                            'name': 'Wikipedia',
                            'disambiguation': target.netloc.split('.')[0] + ':' +
                                              target.path.split('/')[2].replace("_", " "),
                            'icon': 'wikipedia-16.png',
                        }.items()))
                else:
                    # TODO: Process other types here
                    pass
            except Exception as e:
                # TODO: Log error
                pass
    external_urls.sort()
    return external_urls
