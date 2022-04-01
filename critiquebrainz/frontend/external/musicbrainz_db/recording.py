from brainzutils import cache
from brainzutils.musicbrainz_db import recording as db
from brainzutils.musicbrainz_db import serialize
from brainzutils.musicbrainz_db import unknown_entities

from critiquebrainz.frontend.external.musicbrainz_db import DEFAULT_CACHE_EXPIRATION


def recording_is_unknown(recording):
    return recording['name'] == unknown_entities.unknown_recording.name


def get_recording_by_id(mbid):
    """Get recording with MusicBrainz ID.

    Args:
        mbid (uuid): MBID(gid) of the recording.
    Returns:
        Dictionary containing the recording information
    """
    key = cache.gen_key('recording', mbid)
    recording = cache.get(key)
    if not recording:
        recording = db.get_recording_by_mbid(
            mbid,
            includes=['artists', 'work-rels', 'url-rels'],
            unknown_entities_for_missing=True,
        )
        if recording_is_unknown(recording):
            return None
        cache.set(key=key, val=recording, time=DEFAULT_CACHE_EXPIRATION)
    return recording
