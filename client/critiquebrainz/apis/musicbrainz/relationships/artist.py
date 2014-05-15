def process(artist):
    """Handles processing supported relation lists."""
    if 'artist-relation-list' in artist and artist['artist-relation-list']:
        artist['band-members'] = _artist(artist['artist-relation-list'])
    elif 'url-relation-list' in artist and artist['url-relation-list']:
        artist['url-relation-list'] = _url(artist['url-relation-list'])
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
        'wikipedia': {'name': 'Wikipedia', 'icon': 'wikipedia-16.png', },
        'wikidata': {'name': 'Wikidata', 'icon': 'wikidata-16.png', },
        'discogs': {'name': 'Discogs', 'icon': 'discogs-16.png', },
        'allmusic': {'name': 'Allmusic', 'icon': 'allmusic-16.png', },
        'bandcamp': {'name': 'Bandcamp', 'icon': 'bandcamp-16.png', },
        'lyrics': {'name': 'Lyrics', },
        'official homepage': {'name': 'Official homepage', },
        'BBC Music page': {'name': 'BBC Music', },
    }
    processed = []
    for relation in list:
        if relation['type'] in basic_types:
            processed.append(dict(relation.items() + basic_types[relation['type']].items()))
        else:
            # TODO: Process other types here
            pass
    return processed