from brainzutils import cache
from brainzutils.musicbrainz_db.label import fetch_multiple_labels
from critiquebrainz.frontend.external.musicbrainz_db import DEFAULT_CACHE_EXPIRATION
from critiquebrainz.frontend.external.relationships import label as label_rel


def get_label_by_id(mbid):
    """Get label with MusicBrainz ID.

    Args:
        mbid (uuid): MBID(gid) of the label.
    Returns:
        Dictionary containing the label information
    """
    key = cache.gen_key(mbid)
    label = cache.get(key)
    if not label:
        label = fetch_multiple_labels(
            [mbid],
            includes=['artist-rels', 'url-rels'],
        ).get(mbid)
        cache.set(key=key, val=label, time=DEFAULT_CACHE_EXPIRATION)
    return label_rel.process(label)
