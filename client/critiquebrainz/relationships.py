def process_relationship(type_a, type_b, list=[]):
    supported_types = supported_relations[type_a][type_b]
    processed = []
    for relation in list:
        if relation['type'] in supported_types:
            rel_type = supported_types[relation['type']]
            processed.append(dict(relation.items() + rel_type.items()))
    return processed


# All advanced relationships supported by CritiqueBrainz are defined here.
supported_relations = {
    'release-group': {
        'url': {
            'wikipedia': {
                'name': 'Wikipedia',
                'icon': 'wikipedia-16.png',
            },
            'wikidata': {
                'name': 'Wikidata',
                'icon': 'wikidata-16.png',
            },
            'discogs': {
                'name': 'Discogs',
                'icon': 'discogs-16.png',
            },
            'allmusic': {
                'name': 'Allmusic',
                'icon': 'allmusic-16.png',
            },
            'lyrics': {
                'name': 'Lyrics',
            },
            'official homepage': {
                'name': 'Official homepage',
            },
            'recording studio': {
                'name': 'Recording studio',
            },
        },
    },
}
