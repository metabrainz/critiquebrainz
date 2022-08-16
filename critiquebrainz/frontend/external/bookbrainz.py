import requests
from critiquebrainz.frontend.external.bookbrainz_db.edition_group import fetch_multiple_edition_groups
from critiquebrainz.frontend.external.bookbrainz_db.literary_work import fetch_multiple_literary_works
from critiquebrainz.frontend.external.bookbrainz_db.author import fetch_multiple_authors

BASE_URL = 'https://bookbrainz.org/search/search'

MAP_BB_ENTITY_TYPE = {
    'bb_edition_group': 'EditionGroup',
    'bb_literary_work': 'Work',
    'bb_author': 'Author',
}

def fetch_bb_data(entity_type, bbids):
    if entity_type == 'bb_edition_group':
        return fetch_multiple_edition_groups(bbids).values()
    elif entity_type == 'bb_literary_work':
        return fetch_multiple_literary_works(bbids).values()
    elif entity_type == 'bb_author':
        return fetch_multiple_authors(bbids).values()


def search_bookbrainz_entities(entity_type, query='', limit=None, offset=None):
    bb_entity_type = MAP_BB_ENTITY_TYPE[entity_type]
    params = {'q': query, 'type': bb_entity_type, 'size': limit, 'from': offset}
    data = requests.get(BASE_URL, params=params, timeout=5)
    data.raise_for_status()
    data = data.json()
    count = data['total']
    results = data['results']
    bbids = [result["bbid"] for result in results]
    entity_data = fetch_bb_data(entity_type, bbids)
    return count, entity_data
