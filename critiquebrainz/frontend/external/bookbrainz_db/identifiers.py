from typing import List
from brainzutils import cache
import sqlalchemy
import critiquebrainz.frontend.external.bookbrainz_db as db
from critiquebrainz.frontend.external.bookbrainz_db import DEFAULT_CACHE_EXPIRATION

def fetch_identifiers(identifier_set_id: int) -> List:
    """
    Fetch identifiers from the database.
    Args:
        identifier_set_id (int): Identifier set ID.
    Returns:
        List of identifiers.
    """
    if not identifier_set_id:
        return None
    
    key = cache.gen_key('identifier', identifier_set_id)
    identifiers = cache.get(key)
    if not identifiers:
        with db.bb_engine.connect() as connection:
            result = connection.execute(sqlalchemy.text("""
                SELECT
                    iden.type_id as type_id,
                    idtype.label as label,
                    iden.value as value
                FROM bookbrainz.identifier_set__identifier idens
                LEFT JOIN bookbrainz.identifier iden on idens.identifier_id = iden.id
                LEFT JOIN bookbrainz.identifier_type idtype on iden.type_id = idtype.id
                WHERE idens.set_id = :identifier_set_id;
                """), ({'identifier_set_id': identifier_set_id}))
            identifiers = result.fetchall()
            identifiers = [dict(identifier) for identifier in identifiers]
            identifiers = process_identifiers(identifiers)
            cache.set(key, identifiers, DEFAULT_CACHE_EXPIRATION)

    if not identifiers:
        return None
    return identifiers


def process_identifiers(identifiers: List) -> List:
    """Process identifiers and include urls."""
    external_urls = []

    url_map = {
        1: "https://musicbrainz.org/release/",
        2: "https://musicbrainz.org/artist/",
        3: "https://musicbrainz.org/work/",
        4: "https://www.wikidata.org/wiki/",
        5: "https://www.amazon.com/dp/",
        6: "https://openlibrary.org/books/",
        8: "https://openlibrary.org/works/",
        9: "https://isbnsearch.org/isbn/",
        10: "https://isbnsearch.org/isbn/",
        11: "https://www.barcodelookup.com/",
        12: "https://viaf.org/viaf/",
        29: "https://viaf.org/viaf/",
        31: "https://viaf.org/viaf/",
        13: "http://www.isni.org/",
        14: "https://www.librarything.com/work/",
        15: "https://www.librarything.com/author/",
        16: "https://www.imdb.com/title/",
        17: "https://musicbrainz.org/label/",
        18: "https://www.wikidata.org/wiki/",
        19: "https://www.wikidata.org/wiki/",
        20: "https://www.wikidata.org/wiki/",
        21: "https://www.wikidata.org/wiki/",
        30: "https://www.wikidata.org/wiki/",
        22: "https://www.archive.org/details/",
        23: "https://www.openlibrary.org/authors/",
        24: "https://lccn.loc.gov/",
        25: "https://www.orcid.org/",
        26: "https://www.worldcat.org/oclc/",
        27: "https://www.goodreads.com/author/show/",
        28: "https://www.goodreads.com/book/show/",
        32: "https://musicbrainz.org/series/",
        33: "https://www.goodreads.com/series/",
        34: "https://www.imdb.com/list/",
    }
    

    icon_map = {
        1: "musicbrainz-16.svg",
        2: "musicbrainz-16.svg",
        3: "musicbrainz-16.svg",
        4: "wikidata-16.png",
        12: "viaf-16.png",
        29: "viaf-16.png",
        31: "viaf-16.png",
        14: "librarything-16.png",
        15: "librarything-16.png",
        16: "imdb-16.png",
        17: "musicbrainz-16.svg",
        18: "wikidata-16.png",
        19: "wikidata-16.png",
        20: "wikidata-16.png",
        21: "wikidata-16.png",
        30: "wikidata-16.png",
        32: "musicbrainz-16.svg",
        34: "imdb-16.png",
    }
    
    for identifier in identifiers:
        value = identifier['value']
        type_id = identifier['type_id']
        if type_id == 13: 
            url = url_map[13] + value.replace(" ", "") # Remove spaces first (see BB-499)
        else:
            url = url_map[type_id] + value
        
        if type_id in icon_map:
            icon = icon_map[type_id]
        else:
            icon = None
        external_urls.append({
            'name': identifier['label'],
            'url': url,
            'value': value,
            'icon': icon,
        })

    return external_urls
