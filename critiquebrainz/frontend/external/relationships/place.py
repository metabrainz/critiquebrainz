from flask_babel import lazy_gettext


PLACE_PLACE_PARTS_REL_ID = 'ff683f48-eff1-40ab-a58f-b128098ffe92'


def process(place):
    """Handles processing supported relation lists."""

    if 'url-rels' in place and place['url-rels']:
        place['external-urls'] = _url(place['url-rels'])

    place_rels = place.pop('place-rels', [])
    parts = _place_place_rels(place_rels, PLACE_PLACE_PARTS_REL_ID, 'forward')
    part_of = _place_place_rels(place_rels, PLACE_PLACE_PARTS_REL_ID, 'backward')
    if parts:
        place['parts'] = parts
    if part_of:
        place['part-of'] = part_of
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


def _place_place_rels(place_list, rel_type, rel_direction):
    """Processor for Place-Place relationship."""
    return [relation for relation in place_list if relation['direction'] == rel_direction and relation['type-id'] == rel_type]
