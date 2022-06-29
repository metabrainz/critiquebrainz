from typing import List
import sqlalchemy
import critiquebrainz.frontend.external.bookbrainz_db as db

def fetch_author_credits(author_credit_id: int) -> List:
    """
    Get info related to an author credit using its ID.
    Args:
        author_credit_id : ID of the author credit.
    Returns:
        A list of dictionaries containing the basic information related to the author credit.
    """

    if not author_credit_id:
        return None

    with db.bb_engine.connect() as connection:
        result = connection.execute(sqlalchemy.text("""
            SELECT* FROM author_credit_name WHERE author_credit_id = :author_credit_id;
            """), {'author_credit_id': author_credit_id})
        author_credits = result.fetchall()

        if not author_credits:
            return None

        result = []
        for author_credit in author_credits:
            author_credit = dict(author_credit)
            author_credit['author_bbid'] = str(author_credit['author_bbid'])
            result.append(author_credit)
        
        result = sorted(result, key = lambda author_credit: author_credit['position'])
        return result
