"""
Methods here define logs for various activities that the moderators can take
via the moderator interface. A new log entry is created for every action.
"""
from datetime import datetime
from critiquebrainz import db
import sqlalchemy


ACTION_HIDE_REVIEW = "hide_review"
ACTION_BLOCK_USER = "block_user"


def create(*, admin_id, review_id=None, user_id=None,
           action, reason):
    """Make a record in the moderation log.

    Args:
        admin_id (uuid): ID of the admin.
        user_id (uuid): ID of the user blocked.
        review_id (uuid): ID of the review hidden.
        action (str): str("hide_review", "block_user").
        reason (str): Reason for blocking a user or hiding a review.
    """
    if not review_id and not user_id:
        raise ValueError("No review ID or user ID specified.")
    if action != ACTION_BLOCK_USER and action != ACTION_HIDE_REVIEW:
        raise ValueError("Please specify a valid action.")
    with db.engine.connect() as connection:
        connection.execute(sqlalchemy.text("""
            INSERT INTO moderation_log(admin_id, user_id, review_id, action, timestamp, reason)
                 VALUES (:admin_id, :user_id, :review_id, :action, :timestamp, :reason)
        """), {
            "admin_id": admin_id,
            "user_id": user_id,
            "review_id": review_id,
            "action": action,
            "timestamp": datetime.now(),
            "reason": reason,
        })


def list_logs(*, admin_id=None, limit=None, offset=None):
    """Get a list of log entries.

    Args:
        admin_id: UUID of the admin whose actions generated the log.
        limit: Maximum number of reviews returned by this method.
        offset: Offset that can be used in conjunction with the limit.

    Returns:
        Pair of values: list of log entries that match applied filters and
        total number of log entries.
    """
    filters = []
    filter_data = {}
    if admin_id is not None:
        filters.append("admin_id = :admin_id")
        filter_data["admin_id"] = admin_id
    filterstr = "AND ".join(filters)
    where_clause = str()
    if filterstr:
        where_clause = "WHERE " + filterstr

    query = sqlalchemy.text("""
        SELECT COUNT(*)
          FROM moderation_log
        {where_clause}
    """.format(where_clause=where_clause))
    with db.engine.connect() as connection:
        result = connection.execute(query, filter_data)
        count = result.fetchone()[0]

    filter_data["limit"] = limit
    filter_data["offset"] = offset

    query = sqlalchemy.text("""
        SELECT moderation_log.id,
               admin_id,
               review_id,
               moderation_log.user_id,
               user_info.display_name as user_name,
               admin_info.display_name as admin_name,
               action,
               timestamp,
               entity_id,
               reason,
               review_user_id,
               review_user_name
          FROM moderation_log
     LEFT JOIN (
                SELECT "user".id,
                       "display_name"
                  FROM "user"
               ) AS admin_info
            ON admin_id = admin_info.id
     LEFT JOIN (
                SELECT review.id as review_uuid,
                       "user".id as review_user_id,
                       "user".display_name as review_user_name,
                       review.entity_id
                  FROM review JOIN "user"
                    ON "user".id = user_id
               ) AS review_info
            ON review_id = review_info.review_uuid
     LEFT JOIN (
                SELECT "user".id,
                       "display_name"
                  FROM "user"
               ) AS user_info
            ON moderation_log.user_id = user_info.id
        {where_clause}
      ORDER BY timestamp DESC
         LIMIT :limit
        OFFSET :offset
    """.format(where_clause=where_clause))

    with db.engine.connect() as connection:
        result = connection.execute(query, filter_data)
        logs = []
        for log in result.fetchall():
            log = dict(log)
            log["user"] = {
                "id": log["user_id"],
                "display_name": log.pop("user_name"),
            }
            log["admin"] = {
                "id": log["admin_id"],
                "display_name": log.pop("admin_name"),
            }
            log["review"] = {
                "id": log["review_id"],
                "entity_id": log.pop("entity_id"),
                "user": {
                    "id": log.pop("review_user_id"),
                    "display_name": log.pop("review_user_name"),
                }
            }
            logs.append(log)
    return logs, count
