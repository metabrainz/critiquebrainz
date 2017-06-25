from flask_babel import lazy_gettext


def process(place):
    """Handles processing supported relation lists."""

    if 'url-rels' in place and place['url-rels']:
        place['external-urls'] = _url(place['url-rels'])

    if 'place-rels' in place and place['place-rels']:
        place['place-rels'] = _place(place['place-rels'])
    return place


def _url(url_list):
    """Processor for Place-URL relationship."""
    basic_types = {
        'wikidata': {
            'name': lazy_gettext('Wikidata'), 'icon': 'wikidata-16.png',
        },
        'discogs': {
            'name': lazy_gettext('Discogs'), 'icon': 'discogs-16.png',
        },
        'last.fm': {
            'name': lazy_gettext('Last.fm'), 'icon': 'lastfm-16.png',
        },
        'official homepage': {
            'name': lazy_gettext('Official homepage'), 'icon': 'home-16.png',
        },
    }
    external_urls = []
    for relation in url_list:
        if relation['type'] in basic_types:
            external_urls.append(dict(list(relation.items()) + list(basic_types[relation['type']].items())))
    return sorted(external_urls, key=lambda k: k['name'])


def _place(place_list):
    """Processor for Place-Place relationship."""
    related_places = []
    for relation in place_list:
        if relation['direction'] == 'backward':
            related_places.append(relation)
    return related_places
