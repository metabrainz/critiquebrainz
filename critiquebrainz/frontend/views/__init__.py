import critiquebrainz.db.avg_rating as db_avg_rating
import critiquebrainz.db.exceptions as db_exceptions

ARTIST_REVIEWS_LIMIT = 5
AUTHOR_REVIEWS_LIMIT = 10
EDITION_GROUP_REVIEWS_LIMIT = 10
LABEL_REVIEWS_LIMIT = 5
LITERARY_WORK_REVIEWS_LIMIT = 10
PLACE_REVIEW_LIMIT = 5
WORK_REVIEWS_LIMIT = 5
RECORDING_REVIEWS_LIMIT = 10
BROWSE_RELEASE_GROUPS_LIMIT = 20
BROWSE_EVENTS_LIMIT = 15
BROWSE_RECORDING_LIMIT = 10


def get_avg_rating(entity_id, entity_type):
    """Retrieve average rating"""
    try:
        return db_avg_rating.get(entity_id, entity_type)
    except db_exceptions.NoDataFoundException:
        return None
