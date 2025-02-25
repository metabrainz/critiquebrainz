from typing import List


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
