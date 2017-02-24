from critiquebrainz import db
from critiquebrainz.db import exceptions as db_exceptions
import sqlalchemy
from critiquebrainz.db import revision as db_revision
from datetime import datetime


def get(user_id, revision_id):
    """Get spam report from the user_id, revision_id.

    Args:
        user_id(uuid): User ID of the reporter.
        revision_id(uuid): Revision ID of the revision of the review.

    Returns:
        Dictionary of the spam report containing the following
        {
            "user_id": (uuid),
            "reason": (str),
            "revision_id": (int),
            "reported_at": (datetime),
            "is_archived": (bool)
        }
    """
    with db.engine.connect() as connection:
        result = connection.execute(sqlalchemy.text("""
           SELECT user_id,
                  reason,
                  revision_id,
                  reported_at,
                  is_archived
             FROM spam_report
            WHERE user_id = :user_id
              AND revision_id = :revision_id
        """), {
            "user_id": user_id,
            "revision_id": revision_id
        })

        report = result.fetchone()
    return dict(report) if report else None


def archive(user_id, revision_id):
    """Archive a Spam Report.

    Args:
        user_id(uuid): ID of the reporter.
        revision_id(uuid): ID of the revision of the reported review.
    """
    with db.engine.connect() as connection:
        connection.execute(sqlalchemy.text("""
            UPDATE spam_report
               SET is_archived = 'true'
             WHERE user_id = :user_id
               AND revision_id = :revision_id
        """), {
            "user_id": user_id,
            "revision_id": revision_id
        })


def create(revision_id, user_id, reason):
    """Create spam report reported by a user on a review.

    Args:
        revision_id(int): ID of the revision of the review whose report is submitted.
        user_id(int): ID of the reporter.
        reason(str): report submitted by a user.

    Returns:
        Dictionary of the spam report containing the following
        {
            "user_id": (uuid),
            "reason": (str),
            "revision_id": (int),
            "reported_at": (datetime),
            "is_archived": (bool)
        }
    """
    with db.engine.connect() as connection:
        connection.execute(sqlalchemy.text("""
            INSERT INTO spam_report
                 VALUES (:user_id, :reason, :revision_id, :reported_at, :is_archived)
            """), {
                "user_id": str(user_id),
                "reason": reason,
                "revision_id": revision_id,
                "reported_at": datetime.now(),
                "is_archived": False
            })
    return get(user_id, revision_id)


def list_reports(**kwargs):
    """Returns the list of reports submitted by users on reviews.

    Args:
        inc_archived(bool, optional): True if archived spam reports to be included.
        review_id(uuid, optional): Specify review ID to list all its spam reports.
        user_id(uuid, optional): Specify user ID to list all spam report by a user.
        offset(int, optional): The number of spam reports to skip from top.
        limit(int, optional): The number of spam reports to select.

    Returns:
        List of dictionaries of spam reports with the following structure:
        {
            "user_id": (uuid),
            "reason": (str),
            "revision_id": (int),
            "reported_at": (datetime),
            "is_archived": (bool)
        }
    """
    filters = []
    filter_data = {}

    if "inc_archived" in kwargs:
        inc_archived = kwargs.pop("inc_archived")
        if not inc_archived:
            filters.append("is_archived = :is_archived")
            filter_data["is_archived"] = inc_archived

    if "review_id" in kwargs:
        review_id = kwargs.pop("review_id")
        filters.append("revision_id IN :revision_ids")
        filter_data["revision_ids"] = tuple([revision['id'] for revision in db_revision.get(review_id, limit=None)])

    if "user_id" in kwargs:
        filters.append("user_id = :user_id")
        filter_data["user_id"] = kwargs.pop("user_id")

    filter_data["offset"] = kwargs.pop("offet", None)
    filter_data["limit"] = kwargs.pop("limit", None)
    if kwargs:
        raise TypeError('Unexpected **kwargs: %r' % kwargs)

    filterstr = "AND".join(filters)
    if filterstr:
        # Use WHERE only when there is data to filter.
        query = sqlalchemy.text("""SELECT user_id,
                                          reason,
                                          revision_id,
                                          reported_at,
                                          is_archived
                                     FROM spam_report
                                    WHERE {}
                                   OFFSET :offset
                                    LIMIT :limit
                """.format(filterstr))
    else:
        query = sqlalchemy.text("""SELECT user_id,
                                          reason,
                                          revision_id,
                                          reported_at,
                                          is_archived
                                     FROM spam_report
                                   OFFSET :offset
                                    LIMIT :limit
                """)
    with db.engine.connect() as connection:
        result = connection.execute(query, filter_data)
        rows = result.fetchall()
        rows = [dict(row) for row in rows]
    return rows, len(rows)
