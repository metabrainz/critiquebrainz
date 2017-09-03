import critiquebrainz.db.avg_rating as db_avg_rating
import critiquebrainz.db.exceptions as db_exceptions

def get_avg_rating(entity_id, entity_type):
    """Retrieve average rating"""
    try:
        return db_avg_rating.get(entity_id, entity_type)
    except db_exceptions.NoDataFoundException:
        return None
