def process(release_group):
    """Handles processing supported relation lists."""
    if 'url-relation-list' in release_group and release_group['url-relation-list']:
        release_group['url-relation-list'] = _url(release_group['url-relation-list'])
    return release_group


def _url(list):
    """Processor for Release Group-URL relationship."""
    basic_types = {
        'wikipedia': {'name': 'Wikipedia', 'icon': 'wikipedia-16.png', },
        'wikidata': {'name': 'Wikidata', 'icon': 'wikidata-16.png', },
        'discogs': {'name': 'Discogs', 'icon': 'discogs-16.png', },
        'allmusic': {'name': 'Allmusic', 'icon': 'allmusic-16.png', },
        'lyrics': {'name': 'Lyrics', },
        'official homepage': {'name': 'Official homepage', },
        'recording studio': {'name': 'Recording studio', },
    }
    processed = []
    for relation in list:
        if relation['type'] in basic_types:
            processed.append(dict(relation.items() + basic_types[relation['type']].items()))
        else:
            # TODO: Process other types here
            pass
    return processed
