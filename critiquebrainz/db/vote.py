from datetime import datetime

import sqlalchemy

from critiquebrainz import db
from critiquebrainz.db import exceptions as db_exceptions


def get(user_id, revision_id):
    """Get vote cast by a user on a revision.

    Args:
        user_id (uuid): ID of a user.
        revision_id (id): ID of a review revision that the vote is associated with.

    Returns:
        Dictionary with the following structure:
        {
            "user_id": (uuid),
            "revision_id": (int),
            "vote": (bool),
            "rated_at": (datetime)
        }
    """
    with db.engine.connect() as connection:
        result = connection.execute(sqlalchemy.text("""
            SELECT user_id, revision_id, vote, rated_at
              FROM vote
             WHERE user_id = :user_id AND revision_id = :revision_id
        """), {
            "user_id": user_id,
            "revision_id": revision_id,
        })
        row = result.mappings().first()
        if not row:
            raise db_exceptions.NoDataFoundException("Cannot find specified vote.")
        return dict(row)


def submit(user_id, revision_id, vote):
    """Set user's vote for a revision.

    If user already voted on this revision, existing vote value is updated.

    Args:
        user_id (uuid): ID of a user.
        revision_id (id): ID of a review revision that the vote is associated with.
        vote (bool): `False` if it's a negative vote, `True` if positive.
    """
    with db.engine.begin() as connection:
        connection.execute(sqlalchemy.text("""
            INSERT INTO vote (user_id, revision_id, vote, rated_at)
                 VALUES (:user_id, :revision_id, :vote, :rated_at)
            ON CONFLICT (user_id, revision_id) DO UPDATE SET vote = EXCLUDED.vote;
        """), {
            "user_id": user_id,
            "revision_id": revision_id,
            "vote": vote,
            "rated_at": datetime.utcnow(),
        })


def delete(user_id, revision_id):
    """Delete vote cast by a user on a revision.

    Args:
        user_id (uuid): ID of a user.
        revision_id (id): ID of a review revision that the vote is associated with.
    """
    with db.engine.begin() as connection:
        connection.execute(sqlalchemy.text("""
            DELETE FROM vote
                  WHERE user_id = :user_id AND revision_id = :revision_id
        """), {
            "user_id": user_id,
            "revision_id": revision_id,
        })


def get_count():
    """Get the total number of votes in CritiqueBrainz.
    """
    with db.engine.connect() as connection:
        result = connection.execute(sqlalchemy.text("""
            SELECT count(*)
              FROM vote
        """))
        return result.fetchone().count
