def process_relationship(type_a, type_b, list=[]):
    supported_types = supported_relations[type_a][type_b]
    new_rels = []
    for relation in list:
        if relation['type'] in supported_types:
            rel_type = supported_types[relation['type']]
            new_rels.append({
                'type': relation['type'],
                'type-id': relation['type-id'],
                'target': relation['target'],
                'name': rel_type['name'],
            })
    return new_rels


supported_relations = {
    'release-group': {
        'url': {
            'wikipedia': {
                'id': '6578f0e9-1ace-4095-9de8-6e517ddb1ceb',
                'name': 'Wikipedia'
            },
            'wikidata': {
                'id': 'b988d08c-5d86-4a57-9557-c83b399e3580',
                'name': 'Wikidata'
            },
            'discogs': {
                'id': '99e550f3-5ab4-3110-b5b9-fe01d970b126',
                'name': 'Discogs'
            },
            'allmusic': {
                'id': 'a50a1d20-2b20-4d2c-9a29-eb771dd78386',
                'name': 'Allmusic'
            },
            'lyrics': {
                'id': '156344d3-da8b-40c6-8b10-7b1c22727124',
                'name': 'Lyrics'
            },
            'official homepage': {
                'id': '87d97dfc-3206-42fd-89d5-99593d5f1297',
                'name': 'Official homepage'
            },
            'recording studio': {
                'id': 'b17e54df-dcff-4ce3-9ab6-83f4bc0ec50b',
                'name': 'Recording studio'
            },
        },
    },
}