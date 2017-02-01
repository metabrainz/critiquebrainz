from critiquebrainz import db
from critiquebrainz.db import exceptions as db_exceptions
import sqlalchemy


def get(review_id):
    """Get revisions on a review ordered by the timestamp

    Args:
        review_id (uuid): ID of review

    Returns:
        List of dictionaries of revisions of the review
        with the following structure:
        {
            "id": (int),
            "review_id": (uuid),
            "timestamp": (datetime),
            "text": (string)
        }

        and the number(count) of reviews
    """
    with db.engine.connect() as connection:
        result = connection.execute(sqlalchemy.text("""
            SELECT id, review_id, timestamp, text
              FROM revision
             WHERE review_id = :review_id
          ORDER BY timestamp DESC
        """), {
            "review_id": review_id,
        })

        rows = result.fetchall()
        if not rows:
            raise db_exceptions.NoDataFoundException("Cannot find specified review.")
        rows = [dict(row) for row in rows]
        count = len(rows)
    return rows, count


def get_votes(review_id):
    """Get vote count for the all revisions of a review

    Args:
        review_id (uuid): ID of a review

    Returns:
        Dictionary of revisions of a review with a dictionary
        of count of positive and negative votes.
        {
            "revision.id":"{"positive": (int), "negative": (int)}"
        }
    """
    with db.engine.connect() as connection:
        result = connection.execute(sqlalchemy.text("""
            SELECT DISTINCT revision.id, user_id, vote, timestamp
                       FROM revision
                  LEFT JOIN vote
                         ON vote.revision_id = revision.id
                      WHERE review_id = :review_id
                   ORDER BY timestamp DESC
        """),{
            "review_id": review_id,
        })

        rows = result.fetchall()
        if not rows:
            raise db_exceptions.NoDataFoundException("Cannot find votes for review(ID: {})".format(review_id))
        votes = dict()
        for row in rows:
            revision = row.id
            if revision not in votes:
                votes[revision] = {'positive':0, 'negative':0}
            if row.vote == False:
                votes[revision]['negative'] += 1
            elif row.vote == True:
                votes[revision]['positive'] += 1
    return votes
