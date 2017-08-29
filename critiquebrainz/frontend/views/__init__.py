import critiquebrainz.db.avg_rating as db_avg_rating
import critiquebrainz.db.exceptions as db_exceptions

def get_avg_rating(entity_id, entity_type):
    """Retrieve avg_rating and convert rating on a scale 1-5."""
    try:
        avg_rating = db_avg_rating.get(entity_id, entity_type)
        avg_rating["rating"] = round(avg_rating["rating"] / 20, 1)
    except db_exceptions.NoDataFoundException:
        avg_rating = None

    return avg_rating
