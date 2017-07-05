from collections import defaultdict
from brainzutils import cache
from mbdata import models
from mbdata.utils import get_something_by_gid
from critiquebrainz.frontend.external.musicbrainz_db import mb_session
from critiquebrainz.frontend.external.musicbrainz_db.helpers import get_relationship_info
from critiquebrainz.frontend.external.musicbrainz_db.serialize import to_dict_release_groups
from critiquebrainz.frontend.external.musicbrainz_db.includes import check_includes
import critiquebrainz.frontend.external.musicbrainz_db.exceptions as mb_exceptions
import critiquebrainz.frontend.external.relationships.release_group as release_group_rel


DEFAULT_CACHE_EXPIRATION = 12 * 60 * 60 # seconds (12 hours)


def get_release_group_by_id(mbid):
    """Get release group using the MusicBrainz ID."""
    key = cache.gen_key(mbid)
    release_group = cache.get(key)
    if not release_group:
        release_group = fetch_multiple_release_groups(
            mbids=[mbid],
            includes=['artists', 'releases', 'release-group-rels', 'url-rels', 'work-rels', 'tags']
        )[mbid]
    cache.set(key=key, val=release_group, time=DEFAULT_CACHE_EXPIRATION)
    return release_group_rel.process(release_group)


def fetch_multiple_release_groups(*, mbids, includes=None):
    includes = [] if includes is None else includes
    includes_data = defaultdict(dict)
    check_includes('release_group', includes)
    with mb_session() as db:
        query = db.query(models.ReleaseGroup)
        release_groups = []
        for mbid in mbids:
            release_group = get_something_by_gid(query, models.ReleaseGroupGIDRedirect, mbid)
            if not release_group:
                raise mb_exceptions.NoDataFoundException("Couldn't find a release group with id: {mbid}".format(mbid=mbid))
            release_groups.append(release_group)
        release_group_ids = [release_group.id for release_group in release_groups]

        if 'artists' in includes:
            for release_group in release_groups:
                artist_credit_names = release_group.artist_credit.artists
                includes_data[release_group.id]['artist-credit-names'] = artist_credit_names

        if 'releases' in includes:
            query = db.query(models.Release).filter(getattr(models.Release, "release_group_id").in_(release_group_ids))
            for release in query:
                includes_data[release.release_group_id].setdefault('releases', []).append(release)

        if 'release-group-rels' in includes:
            get_relationship_info(
                db=db,
                target_type='release_group',
                source_type='release_group',
                source_entity_ids=release_group_ids,
                includes_data=includes_data,
            )

        if 'url-rels' in includes:
            get_relationship_info(
                db=db,
                target_type='url',
                source_type='release_group',
                source_entity_ids=release_group_ids,
                includes_data=includes_data,
            )

        if 'work-rels' in includes:
            get_relationship_info(
                db=db,
                target_type='work',
                source_type='release_group',
                source_entity_ids=release_group_ids,
                includes_data=includes_data,
            )

        if 'tags' in includes:
            query = db.query(models.ReleaseGroup.id, models.Tag.name).\
            join(models.ReleaseGroupTag).\
            join(models.Tag).filter(models.ReleaseGroup.id.in_(release_group_ids))
            for release_group_id, tag in query:
                includes_data[release_group_id].setdefault('tags', []).append(tag)

        release_groups = {str(release_group.gid): to_dict_release_groups(release_group, includes_data.get(release_group.id, {}))
                          for release_group in release_groups}
        return release_groups
