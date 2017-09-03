from mbdata.utils.models import get_link_target
from critiquebrainz.frontend.external.musicbrainz_db.utils import ENTITY_MODELS


def to_dict_relationships(data, source_obj, relationship_objs):
    """Convert relationship objects to dictionaries.

    Args:
        data (dict): Dictionary containing info of source object.
        source_obj (mbdata.models): object of source entity.
        relationship_objs (dict): Dictionary containing list of objects of different relations.

    Returns:
        Dictionary containing lists of dictionaries of related entities.
    """
    for entity_type in ENTITY_MODELS:
        relation = f'{entity_type}-rels'
        if relation in relationship_objs:
            data[relation] = []
            for obj in relationship_objs[relation]:
                link_data = {
                    'type': obj.link.link_type.name,
                    'type-id': obj.link.link_type.gid,
                    'begin-year': obj.link.begin_date_year,
                    'end-year': obj.link.end_date_year,
                }
                link_data['direction'] = 'forward' if source_obj.id == obj.entity0_id else 'backward'
                if obj.link.ended:
                    link_data['ended'] = True
                link_data[entity_type] = TO_DICT_ENTITIES[entity_type](get_link_target(obj, source_obj))
                data[relation].append(link_data)


def to_dict_areas(area, includes=None):
    if includes is None:
        includes = {}
    data = {
        'id': area.gid,
        'name': area.name,
    }

    if 'relationship_objs' in includes:
        to_dict_relationships(data, area, includes['relationship_objs'])
    return data


def to_dict_artists(artist, includes=None):
    if includes is None:
        includes = {}
    data = {
        'id': artist.gid,
        'name': artist.name,
        'sort_name': artist.sort_name,
    }

    if 'type' in includes and includes['type']:
        data['type'] = includes['type'].name

    if 'relationship_objs' in includes:
        to_dict_relationships(data, artist, includes['relationship_objs'])
    return data


def to_dict_urls(url, includes=None):
    if includes is None:
        includes = {}
    data = {
        'id': url.gid,
        'url': url.url,
    }

    if 'relationship_objs' in includes:
        to_dict_relationships(data, url, includes['relationship_objs'])
    return data


def to_dict_places(place, includes=None):
    if includes is None:
        includes = {}
    data = {
        'id': place.gid,
        'name': place.name,
        'address': place.address,
    }

    if 'type' in includes and includes['type']:
        data['type'] = includes['type'].name

    if place.coordinates:
        data['coordinates'] = {
            'latitude': place.coordinates[0],
            'longitude': place.coordinates[1],
        }

    if 'area' in includes and includes['area']:
        data['area'] = to_dict_areas(includes['area'])

    if 'relationship_objs' in includes:
        to_dict_relationships(data, place, includes['relationship_objs'])
    return data


def to_dict_artist_credit_names(artist_credit_name):
    data = {
        'name': artist_credit_name.name,
        'artist': to_dict_artists(artist_credit_name.artist),
    }
    if artist_credit_name.join_phrase:
        data['join_phrase'] = artist_credit_name.join_phrase
    return data


def to_dict_release_groups(release_group, includes=None):
    if includes is None:
        includes = {}

    data = {
        'id': release_group.gid,
        'title': release_group.name,
    }

    if 'type' in includes and includes['type']:
        data['type'] = includes['type'].name

    if 'artist-credit-phrase' in includes:
        data['artist-credit-phrase'] = includes['artist-credit-phrase']

    if 'meta' in includes and includes['meta'].first_release_date_year:
        data['first-release-year'] = includes['meta'].first_release_date_year

    if 'artist-credit-names' in includes:
        data['artist-credit'] = [to_dict_artist_credit_names(artist_credit_name)
                                 for artist_credit_name in includes['artist-credit-names']]

    if 'releases' in includes:
        data['release-list'] = [to_dict_releases(release) for release in includes['releases']]

    if 'relationship_objs' in includes:
        to_dict_relationships(data, release_group, includes['relationship_objs'])

    if 'tags' in includes:
        data['tag-list'] = includes['tags']
    return data


def to_dict_medium(medium, includes=None):
    if includes is None:
        includes = {}
    data = {
        'name': medium.name,
        'track_count': medium.track_count,
        'position': medium.position,
    }
    if medium.format:
        data['format'] = medium.format.name

    if 'tracks' in includes and includes['tracks']:
        data['track-list'] = [to_dict_track(track) for track in includes['tracks']]
    return data


def to_dict_track(track, includes=None):
    if includes is None:
        includes = {}
    data = {
        'id': track.gid,
        'name': track.name,
        'number': track.number,
        'position': track.position,
        'length': track.length,
        'recording_id': track.recording.gid,
        'recording_title': track.recording.name,
    }
    return data


def to_dict_releases(release, includes=None):
    if includes is None:
        includes = {}

    data = {
        'id': release.gid,
        'name': release.name,
    }

    if 'relationship_objs' in includes:
        to_dict_relationships(data, release, includes['relationship_objs'])

    if 'release-groups' in includes:
        data['release-group'] = to_dict_release_groups(includes['release-groups'])

    if 'media' in includes:
        data['medium-list'] = [to_dict_medium(medium, includes={'tracks': medium.tracks})
                               for medium in includes['media']]
    return data


def to_dict_events(event, includes=None):
    if includes is None:
        includes = {}
    data = {
        'id': event.gid,
        'name': event.name,
    }
    if 'relationship_objs' in includes:
        to_dict_relationships(data, event, includes['relationship_objs'])
    return data


def to_dict_series(series, includes=None):
    if includes is None:
        includes = []
    data = {
        'id': series.gid,
        'name': series.name,
    }
    if 'relationship_objs' in includes:
        to_dict_relationships(data, series, includes['relationship_objs'])
    return data


TO_DICT_ENTITIES = {
    'artist': to_dict_artists,
    'url': to_dict_urls,
    'place': to_dict_places,
    'release_group': to_dict_release_groups,
    'area': to_dict_areas,
    'release': to_dict_releases,
    'event': to_dict_events,
    'series': to_dict_series,
    'medium': to_dict_medium,
}
