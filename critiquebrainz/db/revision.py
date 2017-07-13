from critiquebrainz import db
from critiquebrainz.db import exceptions as db_exceptions
import sqlalchemy
from datetime import datetime


def get(review_id, limit=1, offset=0):
    """Get revisions on a review ordered by the timestamp

    Args:
        review_id (uuid): ID of review
        limit (int): The number of revisions to return(default=1)
        offset (int): The number of revisions to skip from top(default=0)

    Returns:
        List of dictionaries of revisions of the review
        with the following structure:
        {
            "id": (int),
            "review_id": (uuid),
            "timestamp": (datetime),
            "text": (string),
            "votes_positive": (int),
            "votes_negative": (int),
        }
    """
    with db.engine.connect() as connection:
        result = connection.execute(sqlalchemy.text("""
            SELECT id,
                   review_id,
                   timestamp,
                   text,
                   SUM(
                       CASE WHEN vote='t' THEN 1 ELSE 0 END
                   ) AS votes_positive,
                   SUM(
                       CASE WHEN vote='f' THEN 1 ELSE 0 END
                   ) AS votes_negative
              FROM revision
         LEFT JOIN vote
                ON vote.revision_id = revision.id
             WHERE review_id = :review_id
          GROUP BY revision.id
          ORDER BY timestamp DESC
            OFFSET :offset
             LIMIT :limit
        """), {
            "review_id": review_id,
            "offset": offset,
            "limit": limit
        })

        rows = result.fetchall()
        if not rows:
            raise db_exceptions.NoDataFoundException("Cannot find specified review.")
        rows = [dict(row) for row in rows]
    return rows


def get_count(review_id):
    """Get total number of revisions of a review

    Args:
        review_id (uuid): ID of a review

    Returns:
        count (int): Total number of revisions of a review
    """
    with db.engine.connect() as connection:
        result = connection.execute(sqlalchemy.text("""
            SELECT count(*)
              FROM revision
             WHERE review_id = :review_id
        """), {
            "review_id": review_id
        })
        count = result.fetchone()[0]
    return count


def get_all_votes(review_id):
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
        """), {
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


def get_revision_number(review_id, revision_id):
    """Get revision number of the review from the revision_id.

    Args:
        review_id (uuid): ID of the review.
        revision_id (int): ID of the revision whose number is to be fetched.

    Returns:
        rev_num(int): revision number of the revision.
    """
    with db.engine.connect() as connection:
        result = connection.execute(sqlalchemy.text("""
            SELECT row_number
              FROM (
                 SELECT row_number() over(order by timestamp),
                        id
                   FROM revision
                  WHERE review_id = :review_id
             ) AS indexed_revisions
             WHERE id = :revision_id
        """), {
            "review_id": review_id,
            "revision_id": revision_id,
        })
        rev_num = result.fetchone()[0]
        if not rev_num:
            raise db_exceptions.NoDataFoundException("Can't find the revision with id={} for specified review.".format(revision_id))
    return rev_num


def create(review_id, text):
    """Creates a new revision for the given review.

    Args:
        review_id (uuid): ID of the review.
        text (str): Updated/New text of the review.
    """
    with db.engine.connect() as connection:
        connection.execute(sqlalchemy.text("""
            INSERT INTO revision(review_id, timestamp, text)
                 VALUES (:review_id, :timestamp, :text)
        """), {
            "review_id": review_id,
            "timestamp": datetime.now(),
            "text": text,
        })


def votes(revision_id):
    """Get votes of a particular revision.

    Args:
        revision_id (int): ID of a revision.
    Returns:
        Dict with the following structure:
        {
            "positive": int,
            "negative: int,
        }
    """
    with db.engine.connect() as connection:
        result = connection.execute(sqlalchemy.text("""
            SELECT vote
              FROM revision
              JOIN vote
                ON vote.revision_id = revision.id
             WHERE revision.id = :revision_id
        """), {
            "revision_id": revision_id,
        })

        votes = result.fetchall()
        revision_votes = {"positive": 0, "negative": 0}
        for vote in votes:
            if vote.vote == True:
                revision_votes["positive"] += 1
            elif vote.vote == False:
                revision_votes["negative"] += 1
    return revision_votes
