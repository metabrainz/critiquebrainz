from brainzutils import cache
from brainzutils.musicbrainz_db import recording as db

from critiquebrainz.frontend.external.musicbrainz_db import DEFAULT_CACHE_EXPIRATION


def get_recording_by_id(mbid):
    """Get recording with MusicBrainz ID.

    Args:
        mbid (uuid): MBID(gid) of the recording.
    Returns:
        Dictionary containing the recording information
    """
    key = cache.gen_key(mbid)
    recording = cache.get(key)
    if not recording:
        recording = db.get_recording_by_id(
            mbid,
            includes=['artists', 'work-rels', 'url-rels'],
        )
        cache.set(key=key, val=recording, time=DEFAULT_CACHE_EXPIRATION)
    return recording
