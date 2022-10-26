from datetime import datetime

import sqlalchemy

from critiquebrainz import db
from critiquebrainz.db import VALID_RATING_VALUES, RATING_SCALE_1_5, RATING_SCALE_0_100
from critiquebrainz.db import avg_rating as db_avg_rating
from critiquebrainz.db import exceptions as db_exceptions
from critiquebrainz.db import review as db_review


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
            "rating": (int),
            "votes_positive": (int),
            "votes_negative": (int),
        }
    """
    with db.engine.begin() as connection:
        result = connection.execute(sqlalchemy.text("""
            SELECT id,
                   review_id,
                   timestamp,
                   text,
                   rating,
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

        rows = result.mappings().all()
        if not rows:
            raise db_exceptions.NoDataFoundException("Cannot find specified review.")
        rows = [dict(row) for row in rows]
        # Convert ratings to values on a scale 1-5
        for row in rows:
            row["rating"] = RATING_SCALE_1_5.get(row["rating"])
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
                votes[revision] = {'positive': 0, 'negative': 0}
            if row.vote:  # True = positive
                votes[revision]['positive'] += 1
            else:  # False = negative
                votes[revision]['negative'] += 1
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
        rev_num = result.fetchone()
        if not rev_num:
            raise db_exceptions.NoDataFoundException("Can't find the revision with id={} for specified review.".
                                                     format(revision_id))
    return rev_num[0]


def create(connection, review_id, text=None, rating=None):
    """Creates a new revision for the given review.

    Args:
        connection: connection to database to update/create the review
        review_id (uuid): ID of the review.
        text (str): Updated/New text part of the review.
        rating (int): Updated/New rating part of the review
    """
    if text is None and rating is None:
        raise db_exceptions.BadDataException("Text part and rating part of a revision can not be None simultaneously")
    if rating not in VALID_RATING_VALUES:
        raise ValueError("{} is not a valid rating value. It must be on the scale 1-5".format(rating))
    # Convert ratings to values on a scale 0-100
    rating = RATING_SCALE_0_100.get(rating)

    query = sqlalchemy.text("""INSERT INTO revision(review_id, timestamp, text, rating)
        VALUES (:review_id, :timestamp, :text, :rating)""")
    params = {
        "review_id": review_id,
        "timestamp": datetime.now(),
        "text": text,
        "rating": rating,
    }

    connection.execute(query, params)


def update_rating(review_id):
    # Update average rating if rating part of the review has changed
    review = db_review.get_by_id(review_id)
    rev_num = get_revision_number(review["id"], review["last_revision"]["id"])
    if rev_num > 1:
        revisions = get(review["id"], limit=2, offset=0)
        if revisions[0]["rating"] != revisions[1]["rating"]:
            db_avg_rating.update(review["entity_id"], review["entity_type"])
    else:
        db_avg_rating.update(review["entity_id"], review["entity_type"])


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
            if vote.vote:  # True = positive
                revision_votes["positive"] += 1
            else:  # False = negative
                revision_votes["negative"] += 1
    return revision_votes
