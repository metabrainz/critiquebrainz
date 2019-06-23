import critiquebrainz.frontend.external.musicbrainz_db.exceptions as mb_exceptions

RELATABLE_TYPES = [
    'area',
    'artist',
    'label',
    'place',
    'event',
    'recording',
    'release',
    'release-group',
    'series',
    'url',
    'work',
    'instrument'
]
RELATION_INCLUDES = [entity + '-rels' for entity in RELATABLE_TYPES]
TAG_INCLUDES = ["tags", "user-tags"]
RATING_INCLUDES = ["ratings", "user-ratings"]
VALID_INCLUDES = {
    'place': ["aliases", "annotation"] + RELATION_INCLUDES + TAG_INCLUDES,
    'event': ["aliases"] + RELATION_INCLUDES + TAG_INCLUDES,
    'release_group': ["artists", "media", "releases"] + TAG_INCLUDES + RELATION_INCLUDES,
    'release': [
        "artists", "labels", "recordings", "release-groups", "media", "annotation", "aliases"
    ] + TAG_INCLUDES + RELATION_INCLUDES,
    'artist': ["recordings", "releases", "media", "aliases", "annotation"] + RELATION_INCLUDES + TAG_INCLUDES,
}


def check_includes(entity, includes):
    """Check if includes specified for an entity are valid includes."""
    for include in includes:
        if include not in VALID_INCLUDES[entity]:
            raise mb_exceptions.InvalidIncludeError("Bad includes: {inc} is not a valid include".format(inc=include))
