from brainzutils import cache
from brainzutils.musicbrainz_db import label as db

from critiquebrainz.frontend.external.musicbrainz_db import DEFAULT_CACHE_EXPIRATION
from critiquebrainz.frontend.external.relationships import label as label_rel


def get_label_by_mbid(mbid):
    """Get label with MusicBrainz ID.

    Args:
        mbid (uuid): MBID(gid) of the label.
    Returns:
        Dictionary containing the label information
    """
    key = cache.gen_key('label', mbid)
    label = cache.get(key)
    if not label:
        label = db.get_label_by_mbid(
            mbid,
            includes=['artist-rels', 'url-rels'],
        )
        if not label:
            return None
        cache.set(key, label, DEFAULT_CACHE_EXPIRATION)
    return label_rel.process(label)
