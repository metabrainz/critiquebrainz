from collections import defaultdict
from brainzutils import cache
from sqlalchemy.orm import joinedload
from mbdata import models
from critiquebrainz.frontend.external.musicbrainz_db import mb_session, DEFAULT_CACHE_EXPIRATION
from critiquebrainz.frontend.external.musicbrainz_db.helpers import get_relationship_info, get_tags
from critiquebrainz.frontend.external.musicbrainz_db.serialize import to_dict_release_groups
from critiquebrainz.frontend.external.musicbrainz_db.includes import check_includes
from critiquebrainz.frontend.external.musicbrainz_db.utils import get_entities_by_gids
import critiquebrainz.frontend.external.relationships.release_group as release_group_rel


def get_release_group_by_id(mbid):
    """Get release group using the MusicBrainz ID."""
    key = cache.gen_key(mbid)
    release_group = cache.get(key)
    if not release_group:
        release_group = _get_release_group_by_id(mbid)
        cache.set(key=key, val=release_group, time=DEFAULT_CACHE_EXPIRATION)
    return release_group_rel.process(release_group)


def _get_release_group_by_id(mbid):
    return fetch_multiple_release_groups(
        [mbid],
        includes=['artists', 'releases', 'release-group-rels', 'url-rels', 'tags'],
    )[mbid]


def fetch_multiple_release_groups(mbids, *, includes=None):
    includes = [] if includes is None else includes
    includes_data = defaultdict(dict)
    check_includes('release_group', includes)
    with mb_session() as db:
        # Join table meta which contains release date for a release group
        query = db.query(models.ReleaseGroup).options(joinedload("meta"))

        if 'artists' in includes:
            query = query.options(joinedload("artist_credit")).\
                    options(joinedload("artist_credit.artists")).\
                    options(joinedload("artist_credit.artists.artist"))

        release_groups = get_entities_by_gids(
            query=query,
            entity_type='release_group',
            mbids=mbids,
        )
        release_group_ids = [release_group.id for release_group in release_groups.values()]

        if 'artists' in includes:
            for release_group in release_groups.values():
                artist_credit_names = release_group.artist_credit.artists
                includes_data[release_group.id]['artist-credit-names'] = artist_credit_names
                includes_data[release_group.id]['artist-credit-phrase'] = release_group.artist_credit.name

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
            release_group_tags = get_tags(
                db=db,
                entity_model=models.ReleaseGroup,
                tag_model=models.ReleaseGroupTag,
                entity_ids=release_group_ids,
            )
            for release_group_id, tags in release_group_tags:
                includes_data[release_group_id]['tags'] = tags

        for release_group in release_groups.values():
            includes_data[release_group.id]['meta'] = release_group.meta
        release_groups = {str(mbid): to_dict_release_groups(release_groups[mbid], includes_data[release_groups[mbid].id])
                          for mbid in mbids}
        return release_groups
