import requests
from critiquebrainz.frontend.external.bookbrainz_db.edition_group import fetch_multiple_edition_groups
from critiquebrainz.frontend.external.bookbrainz_db.author import fetch_multiple_authors

BASE_URL = 'https://bookbrainz.org/search/search'

def search_edition_group(query='', limit=None, offset=None):
    params = {'q': query, 'type': 'EditionGroup', 'size': limit, 'from': offset}
    data = requests.get(BASE_URL, params=params, timeout=5)
    data.raise_for_status()
    data = data.json()
    count = data['total']
    results = data['results']
    bbids = [result["bbid"] for result in results]
    edition_group_data = fetch_multiple_edition_groups(bbids).values()
    return count, edition_group_data


def search_author(query='', limit=None, offset=None):
    params = {'q': query, 'type': 'Author', 'size': limit, 'from': offset}
    data = requests.get(BASE_URL, params=params, timeout=5)
    data.raise_for_status()
    data = data.json()
    count = data['total']
    results = data['results']
    bbids = [result["bbid"] for result in results]
    author_data = fetch_multiple_authors(bbids).values()
    return count, author_data
