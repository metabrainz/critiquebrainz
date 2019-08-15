import critiquebrainz.db.avg_rating as db_avg_rating
import critiquebrainz.db.exceptions as db_exceptions

ARTIST_REVIEWS_LIMIT = 5
LABEL_REVIEWS_LIMIT = 5
BROWSE_RELEASE_GROUPS_LIMIT = 20


def get_avg_rating(entity_id, entity_type):
    """Retrieve average rating"""
    try:
        return db_avg_rating.get(entity_id, entity_type)
    except db_exceptions.NoDataFoundException:
        return None
