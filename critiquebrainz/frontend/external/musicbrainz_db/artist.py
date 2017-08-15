from collections import defaultdict
from sqlalchemy.orm import joinedload
from mbdata import models
from critiquebrainz.frontend.external.musicbrainz_db import mb_session, DEFAULT_CACHE_EXPIRATION
from critiquebrainz.frontend.external.musicbrainz_db.helpers import get_relationship_info
from critiquebrainz.frontend.external.relationships import artist as artist_rel
from critiquebrainz.frontend.external.musicbrainz_db.utils import get_entities_by_gids
from critiquebrainz.frontend.external.musicbrainz_db.serialize import to_dict_artists
from critiquebrainz.frontend.external.musicbrainz_db.includes import check_includes
from brainzutils import cache


def get_artist_by_id(mbid):
    """Get artist with MusicBrainz ID.

    Args:
        mbid (uuid): MBID(gid) of the artist.
    Returns:
        Dictionary containing the artist information
    """
    key = cache.gen_key(mbid)
    artist = cache.get(key)
    if not artist:
        artist = _get_artist_by_id(mbid)
        cache.set(key=key, val=artist, time=DEFAULT_CACHE_EXPIRATION)
    return artist_rel.process(artist)


def _get_artist_by_id(mbid):
    return fetch_multiple_artists(
        [mbid],
        includes=['artist-rels', 'url-rels'],
    ).get(mbid)


def fetch_multiple_artists(mbids, *, includes=None):
    """Get info related to multiple artists using their MusicBrainz IDs.

    Args:
        mbids (list): List of MBIDs of artists.
        includes (list): List of information to be included.

    Returns:
        Dictionary containing info of multiple artists keyed by their mbid.
    """
    if includes is None:
        includes = []
    includes_data = defaultdict(dict)
    check_includes('artist', includes)
    with mb_session() as db:
        query = db.query(models.Artist).\
                options(joinedload("type"))
        artists = get_entities_by_gids(
            query=query,
            entity_type='artist',
            mbids=mbids,
        )
        artist_ids = [artist.id for artist in artists.values()]

        if 'artist-rels' in includes:
            get_relationship_info(
                db=db,
                target_type='artist',
                source_type='artist',
                source_entity_ids=artist_ids,
                includes_data=includes_data,
            )
        if 'url-rels' in includes:
            get_relationship_info(
                db=db,
                target_type='url',
                source_type='artist',
                source_entity_ids=artist_ids,
                includes_data=includes_data,
            )

    for artist in artists.values():
        includes_data[artist.id]['type'] = artist.type
    artists = {str(mbid): to_dict_artists(artists[mbid], includes_data[artists[mbid].id]) for mbid in mbids}
    return artists
