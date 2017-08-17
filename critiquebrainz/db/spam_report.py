from datetime import datetime
from critiquebrainz import db
from critiquebrainz.db import revision as db_revision
import sqlalchemy


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
            "revision_id": revision_id,
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
            "revision_id": revision_id,
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
            INSERT INTO spam_report (user_id, reason, revision_id, reported_at, is_archived)
                 VALUES (:user_id, :reason, :revision_id, :reported_at, :is_archived)
        """), {
            "user_id": str(user_id),
            "reason": reason,
            "revision_id": revision_id,
            "reported_at": datetime.now(),
            "is_archived": False,
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
            "review": (dict containing id, entity_id, user, last_revision)
            "user": (dict containing id, display_name)
        }
        and the number of spam reports after applying the specified filters.
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

    filterstr = "AND ".join(filters)

    if filterstr:
        # Use WHERE only when there is data to filter.
        filterstr = "WHERE " + filterstr

    query = sqlalchemy.text("""
        SELECT "user".id as reporter_id,
               "user".display_name as reporter_name,
               user_id,
               reason,
               revision_id,
               reported_at,
               is_archived,
               review_uuid,
               review_user_id,
               entity_id,
               review_user_display_name
          FROM "user"
    INNER JOIN (spam_report
               INNER JOIN (revision
                           INNER JOIN (
                           SELECT review.id as review_uuid,
                                  "user".id as review_user_id,
                                  review.entity_id,
                                  "user".display_name as review_user_display_name
                             FROM review
                       INNER JOIN "user"
                               ON "user".id = review.user_id)
                               AS review_detail
                               ON review_id = review_detail.review_uuid)
                       ON spam_report.revision_id = revision.id)
            ON spam_report.user_id = "user".id
            {}
        OFFSET :offset
         LIMIT :limit
    """.format(filterstr))

    with db.engine.connect() as connection:
        result = connection.execute(query, filter_data)
        spam_reports = result.fetchall()
        if spam_reports:
            spam_reports = [dict(spam_report) for spam_report in spam_reports]
            for spam_report in spam_reports:

                spam_report["review"] = {
                    "user": {
                        "id": spam_report.pop("review_user_id"),
                        "display_name": spam_report.pop("review_user_display_name"),
                    },
                    "id": spam_report["review_uuid"],
                    "entity_id": spam_report.pop("entity_id"),
                    "last_revision": db_revision.get(spam_report.pop("review_uuid"))[0],
                }

                spam_report["user"] = {
                    "id": spam_report.pop("reporter_id"),
                    "display_name": spam_report.pop("reporter_name"),
                }
    return spam_reports, len(spam_reports)
