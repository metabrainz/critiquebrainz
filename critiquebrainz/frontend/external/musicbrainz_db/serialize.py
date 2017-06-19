from mbdata.utils.models import ENTITY_TYPES, get_link_target


def to_dict_relationships(data, source_obj, relationship_objs):
    """Convert relationship objects to dictionaries.

    Args:
        data (dict): Dictionary containing info of source object.
        source_obj (mbdata.models): object of source entity.
        relationship_objs (dict): Dictionary containing list of objects of different relations.

    Returns:
        Dictionary containing lists of dictionaries of related entities.
    """
    for entity_type in ENTITY_TYPES:
        relation = '{entity_type}-rels'.format(entity_type=entity_type)
        if relation in relationship_objs:
            data[relation] = []
            for obj in relationship_objs[relation]:
                link_data = {'type': obj.link.link_type.name}
                link_data['direction'] = 'forward' if source_obj.id == obj.entity0_id else 'backward'
                if obj.link.ended:
                    link_data['ended'] = True
                link_data[entity_type] = TO_DICT_ENTITIES[entity_type](get_link_target(obj, source_obj))
                data[relation].append(link_data)


def to_dict_areas(area, includes={}):
    data = {
        'id': area.gid,
        'name': area.name,
    }

    if 'relationship_objs' in includes:
        to_dict_relationships(data, area, includes['relationship_objs'])
    return data


def to_dict_artists(artist, includes={}):
    data = {
        'id': artist.gid,
        'name': artist.name,
        'sort_name': artist.sort_name,
    }

    if 'relationship_objs' in includes:
        to_dict_relationships(data, artist, includes['relationship_objs'])
    return data


def to_dict_urls(url, includes={}):
    data = {
        'id': url.gid,
        'url': url.url,
    }

    if 'relationship_objs' in includes:
        to_dict_relationships(data, url, includes['relationship_objs'])
    return data


def to_dict_places(place, includes={}):
    data = {
        'id': place.gid,
        'name': place.name,
        'address': place.address,
    }

    if place.type:
        data['type'] = place.type.name

    if place.coordinates:
        data['coordinates'] = {
            'latitude': place.coordinates[0],
            'longitude': place.coordinates[1],
        }

    if place.area:
        data['area'] = to_dict_areas(place.area)

    if 'relationship_objs' in includes:
        to_dict_relationships(data, place, includes['relationship_objs'])
    return data


def to_dict_release_groups(release_group, includes={}):
    data = {
        'id': release_group.id,
        'name': release_group.name,
    }
    if 'relationship_objs' in includes:
        to_dict_relationships(data, release_group, includes['relationship_objs'])


TO_DICT_ENTITIES = {
    'artist': to_dict_artists,
    'url': to_dict_urls,
    'place': to_dict_places,
    'release_group': to_dict_release_groups,
    'area': to_dict_areas,
}
