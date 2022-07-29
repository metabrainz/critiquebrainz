from typing import List
from brainzutils import cache
import sqlalchemy
import critiquebrainz.frontend.external.bookbrainz_db as db
from critiquebrainz.frontend.external.bookbrainz_db import DEFAULT_CACHE_EXPIRATION

def fetch_bb_external_identifiers(identifier_set_id: int) -> List:
    """
    Fetch identifiers from the database.
    Args:
        identifier_set_id (int): Identifier set ID.
    Returns:
        List of identifiers containing the following fields:
            - name (str): Identifier name.
            - url (str): Identifier URL.
            - value (str): Identifier value.
            - icon (str): Identifier icon.
    """
    if not identifier_set_id:
        return None
    
    bb_identifiers_key = cache.gen_key('identifier', identifier_set_id)
    identifiers = cache.get(bb_identifiers_key)
    if not identifiers:
        with db.bb_engine.connect() as connection:
            result = connection.execute(sqlalchemy.text("""
                SELECT iden.type_id as type_id,
                       idtype.label as label,
                       idtype.display_template as url_template,
                       iden.value as value
                  FROM identifier_set__identifier idens
             LEFT JOIN identifier iden on idens.identifier_id = iden.id
             LEFT JOIN identifier_type idtype on iden.type_id = idtype.id
                 WHERE idens.set_id = :identifier_set_id
                """), {'identifier_set_id': identifier_set_id})
            identifiers = result.fetchall()
            identifiers = [dict(identifier) for identifier in identifiers]
            identifiers = process_bb_identifiers(identifiers)
            cache.set(bb_identifiers_key, identifiers, DEFAULT_CACHE_EXPIRATION)

    if not identifiers:
        return None
    return identifiers


def process_bb_identifiers(identifiers: List) -> List:
    """Process identifiers and include urls."""
    external_urls = []

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
        url_template = identifier['url_template']

        if type_id == 13: 
            value = value.replace(" ", "") # Remove spaces first (see BB-499)

        url = url_template.format(value=value)

        icon = icon_map.get(type_id, None)
        external_urls.append({
            'name': identifier['label'],
            'url': url,
            'value': value,
            'icon': icon,
        })

    return external_urls
