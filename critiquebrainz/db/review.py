import sqlalchemy
from critiquebrainz import db
from critiquebrainz.db import exceptions as db_exceptions
from brainzutils import cache
from werkzeug.exceptions import BadRequest
from random import shuffle
from flask_babel import lazy_gettext
import critiquebrainz.db.revision as db_revision
from critiquebrainz.db.user import User
import critiquebrainz.db.users as db_users
from critiquebrainz.db.user import User
import uuid

REVIEW_CACHE_NAMESPACE = "Review"
DEFAULT_LICENSE_ID = "CC BY-SA 3.0"
DEFAULT_LANG = "en"
ENTITY_TYPES = [
    'event',
    'place',
    'release_group',
]


def to_dict(review, confidential=False):
    review["user"] = User(db_users.get_by_id(review.pop("user_id")))
    review["user"] = review["user"].to_dict(confidential=True)
    review["id"] = str(review["id"])
    review["entity_id"] = str(review["entity_id"])
    review["last_updated"] = review["last_revision"]["timestamp"]
    review['last_revision']['review_id'] = str(review['last_revision']['review_id'])
    return review


def get_by_id(review_id):
    """Get review from review ID.

    Args:
        review_id(uuid): ID of the review.
    Returns:
        Dictionary with the following structure
        {
            "id": uuid,
            "entity_id": uuid,
            "entity_type": 'release_group', 'event', 'place',
            "user_id": uuid,
            "user": dict,
            "edits": int,
            "is_draft": bool,
            "is_hidden": bool,
            "language": str,
            "license_id": str,
            "source": str,
            "source_url": str,
            "last_revision: dict,
            "votes": dict,
            "rating": int,
            "text": str, "created": datetime,
            "license": dict,
        }
    """
    with db.engine.connect() as connection:
        result = connection.execute(sqlalchemy.text("""
            SELECT review.id AS id,
                   entity_id,
                   entity_type,
                   user_id,
                   edits,
                   is_draft,
                   is_hidden,
                   license_id,
                   language,
                   source,
                   source_url,
                   revision.id AS last_revision_id,
                   timestamp,
                   text,
                   email,
                   "user".created as user_created,
                   display_name,
                   show_gravatar,
                   musicbrainz_id,
                   is_blocked,
                   created_time.created,
                   license.full_name,
                   license.info_url
              FROM review
              JOIN revision
                ON revision.review_id = review.id
              JOIN "user"
                ON "user".id = review.user_id
              JOIN license
                ON license.id = license_id
              JOIN (
                    SELECT review.id,
                           timestamp AS created
                      FROM review
                      JOIN revision
                        ON review.id = revision.review_id
                     WHERE review.id = :review_id
                  ORDER BY revision.timestamp ASC
                     LIMIT 1
                   ) AS created_time
                ON created_time.id = review.id
          ORDER BY timestamp DESC
        """), {
            "review_id": review_id,
        })

        review = result.fetchone()
        if not review:
            raise db_exceptions.NoDataFoundException("No review found with review ID: {}".format(review_id))

        review = dict(review)
        review["last_revision"] = {
            "id": review.pop("last_revision_id"),
            "timestamp": review.pop("timestamp"),
            "text": review.get("text"),
            "review_id": review.get("id"),
        }
        review["user"] = User({
            "id": review["user_id"],
            "display_name": review.pop("display_name", None),
            "is_blocked": review.pop("is_blocked", False),
            "show_gravatar": review.pop("show_gravatar", False),
            "musicbrainz_username": review.pop("musicbrainz_id"),
            "email": review.pop("email"),
            "created": review.pop("user_created"),
        })
        review["license"] = {
            "id": review["license_id"],
            "info_url": review["info_url"],
            "full_name": review["full_name"],
        }
        votes = db_revision.votes(review["last_revision"]["id"])
        review["votes_positive_count"] = votes["positive"]
        review["votes_negative_count"] = votes["negative"]
        review["rating"] = review["votes_positive_count"] - review["votes_negative_count"]
    return review


def hide(review_id):
    """Hide review given the review id.

    Args:
        review_id(uuid): ID of the review to hide.
    """
    with db.engine.connect() as connection:
        connection.execute(sqlalchemy.text("""
            UPDATE review
               SET is_hidden='true'
             WHERE id = :review_id
        """), {
            "review_id": review_id,
        })


def unhide(review_id):
    """Unhide review given the review id.

    Args:
        review_id(uuid): ID of the review to unhide.
    """
    with db.engine.connect() as connection:
        connection.execute(sqlalchemy.text("""
            UPDATE review
               SET is_hidden='fa'
             WHERE id = :review_id
        """), {
            "review_id": review_id,
        })


def get_count(**kwargs):
    """Get number of reviews in CritiqueBrainz.

    Args:
        is_draft (bool): True if drafted reviews are to be counted.
        is_hidden (bool): True if hidden reviews are to be counted.
    """
    is_drafted = kwargs.pop('is_draft', False)
    is_hidden = kwargs.pop('is_hidden', False)
    if(kwargs):
        raise TypeError('Unexpected **kwargs: %r' % kwargs)

    with db.engine.connect() as connection:
        result = connection.execute(sqlalchemy.text("""
            SELECT count(*)
              FROM review
             WHERE is_draft = :is_drafted
               AND is_hidden = :is_hidden
        """), {
            "is_drafted": is_drafted,
            "is_hidden": is_hidden,
        })
        return result.fetchone()[0]


def update(review_id, drafted, **kwargs):
    """Update contents of this review.

    Args:
        review_id (uuid): ID of the review.
        drafted (bool): Whether review is presently drafted.
        license_id(optional, str): Updated license id of a review.
        is_draft(optional, bool): Whether to publish review or keep it drafted.
        text(optional, str): Updated text of a review.
    """

    updates = []
    updated_info = {}

    license_id = kwargs.pop("license_id", None)
    if license_id is not None:
        if not drafted: # If trying to convert published review into draft.
            raise BadRequest(lazy_gettext("Changing licence of a published review is not allowed."))
        updates.append("license_id = :license_id")
        updated_info["license_id"] = license_id

    language = kwargs.pop("language", None)
    if language is not None:
        updates.append("language = :language")
        updated_info["language"] = language

    is_draft = kwargs.pop("is_draft", None)
    if is_draft is not None:
        if not drafted and is_draft: # If trying to convert published review into draft
            raise BadRequest(lazy_gettext("Converting published reviews back to drafts is not allowed."))
        updates.append("is_draft = :is_draft")
        updated_info["is_draft"] = is_draft

    text = kwargs.pop("text")
    if kwargs:
        raise TypeError('Unexpected **kwargs: %r' %kwargs)

    setstr = ", ".join(updates)
    query = sqlalchemy.text("""
        UPDATE review
           SET {}
         WHERE id = :review_id
    """.format(setstr))

    if setstr:
        updated_info["review_id"] = review_id
        with db.engine.connect() as connection:
            connection.execute(query, updated_info)
    # Create new revision
    new_revision = db_revision.create(review_id, text)
    review = get_by_id(review_id)
    cache.invalidate_namespace(REVIEW_CACHE_NAMESPACE)
    return review


def create(**kwargs):
    if 'release_group' in kwargs:
       entity_id = kwargs.pop('release_group')
       entity_type = 'release_group'
    else:
        entity_id = kwargs.pop('entity_id')
        entity_type = kwargs.pop('entity_type')

    with db.engine.connect() as connection:
        result = connection.execute(sqlalchemy.text("""
            BEGIN;
            INSERT INTO review
            VALUES (:id, :entity_id, :entity_type, :user_id, :edits, :is_draft,
            :is_hidden, :license_id, :language, :source, :source_url)
         RETURNING id;
       """), {
           "id": str(uuid.uuid4()),
           "entity_id": entity_id,
           "entity_type": entity_type,
           "user_id": kwargs.pop("user_id"),
           "edits": 0,
           "is_draft": kwargs.pop("is_draft", False),
           "is_hidden": False,
           "language": kwargs.pop("language", DEFAULT_LANG),
           "license_id": kwargs.pop("license_id", DEFAULT_LICENSE_ID),
           "source": kwargs.pop("source", None),
           "source_url": kwargs.pop("source_url", None),
        })
        text = kwargs.pop("text")
        if kwargs:
            connection.execute(sqlalchemy.text("""
                ROLLBACK;
            """))
            raise TypeError("Unexpected **kwargs: %r" % kwargs)
        connection.execute(sqlalchemy.text("""
            COMMIT;
        """))
        review_id = result.fetchone()[0]
        review_revision = db_revision.create(review_id, text)
        cache.invalidate_namespace(REVIEW_CACHE_NAMESPACE)
    return get_by_id(review_id)


def list_reviews(**kwargs):
    """Get a list of reviews.

    This method provides several filters that can be used to select
    specific review. See argument description below for more info.

    Args:
        entity_id: MBID of the entity that is associated with a review.
        entity_type: One of the supported reviewable entities: 'release_group' or 'event', etc.
        user_id: UUID of the author.
        sort: Order of the returned reviews. Can be either "rating" (order by rating), or "created"
            (order by creation time), or "random" (order randomly).
        limit: Maximum number of reviews returned by this method.
        offset: Offset that can be used in conjuction with the limit.
        language: Language (code) of the returned reviews.
        license_id: License of the returned reviews.
        inc_drafts: True if reviews marked as drafts should be included.
            False if not.
        inc_hidden: True if reviews marked as hidden should be included.
            False if not.
        exclude: List of id of reviews to exclude.

    Returns:
        Pair of values: List of reviews that match applied filters
        and total number of reviews.
    """
    filters = []
    filter_data = {}
    inc_drafts = kwargs.pop('inc_drafts', None)
    if not inc_drafts:
        filters.append("is_draft = :is_draft")
        filter_data["is_draft"] = False

    inc_hidden = kwargs.pop('inc_hidden', None)
    if not inc_hidden:
        filters.append("is_hidden = :is_hidden")
        filter_data["is_hidden"] = False

    # FILTERING
    entity_id = kwargs.pop('entity_id', None)
    if entity_id is not None:
        filters.append("entity_id = :entity_id")
        filter_data["entity_id"] = entity_id

    entity_type = kwargs.pop('entity_type', None)
    if entity_type is not None:
        filters.append("entity_type = :entity_type")
        filter_data["entity_type"] = entity_type

    license_id = kwargs.pop('license_id', None)
    if license_id is not None:
        filters.append("license_id = :license_id")
        filter_data["license_id"] = license_id

    user_id = kwargs.pop('user_id', None)
    if user_id is not None:
        filters.append("review.user_id = :user_id")
        filter_data["user_id"] = user_id

    exclude = kwargs.pop('exclude', None)
    if exclude is not None:
        filters.append("review.id NOT IN :exclude")
        filter_data["exclude"] = tuple(exclude)

    language = kwargs.pop('language', None)
    if language is not None:
        filters.append("language = :language")
        filter_data["language"] = language

    filterstr = " AND ".join(filters)
    if filterstr:
        filterstr = " WHERE " + filterstr

    query = sqlalchemy.text("""
        SELECT COUNT(*)
          FROM review
            {}
        """.format(filterstr))

    with db.engine.connect() as connection:
        result = connection.execute(query, filter_data)
        count = result.fetchone()[0]
    sort = kwargs.pop("sort", None)
    order_by_clause = str()

    if sort == 'rating':
        order_by_clause = """
            ORDER BY rating DESC
        """
    elif sort == 'created':
        order_by_clause = """
            ORDER BY created DESC
        """
    elif sort == 'random':
        order_by_clause = """
            ORDER BY RANDOM()
        """
    # Note that all revisions' votes are considered in these ratings
    query = sqlalchemy.text("""
        SELECT review.id,
               entity_id,
               entity_type,
               edits,
               is_draft,
               is_hidden,
               license_id,
               language,
               review.user_id,
               display_name,
               show_gravatar,
               is_blocked,
               email,
               "user".created as user_created,
               musicbrainz_id,
               MIN(revision.timestamp) as created,
               SUM(
                CASE
                 WHEN vote='t' THEN 1
                 ELSE 0
                END
               ) AS votes_positive_count,
               SUM(
                CASE
                 WHEN vote='f' THEN 1
                 ELSE 0
                END
               ) AS votes_negative_count,
               SUM(
                CASE
                 WHEN vote = 't' THEN 1
                 WHEN vote = 'f' THEN -1
                 WHEN vote IS NULL THEN 0
                END
               ) AS rating,
               latest_revision.id as latest_revision_id,
               latest_revision.timestamp as latest_revision_timestamp,
               latest_revision.text as text,
               source,
               source_url,
               license.full_name,
               license.info_url
          FROM review
          JOIN revision
            ON review.id = revision.review_id
     LEFT JOIN vote
            ON vote.revision_id = revision.id
          JOIN "user"
            ON review.user_id = "user".id
          JOIN license
            ON license.id = license_id
          JOIN (
                revision
                JOIN (
                  SELECT review.id AS review_uuid,
                         MAX(timestamp) AS latest_timestamp
                    FROM review
                    JOIN revision
                      ON review.id = review_id
                GROUP BY review.id
                     ) AS latest
                  ON latest.review_uuid = revision.review_id
                 AND latest.latest_timestamp = revision.timestamp
               ) AS latest_revision
            ON review.id = latest_revision.review_id
            {}
      GROUP BY review.id, latest_revision.id, "user".id, license.id
            {}
         LIMIT :limit
        OFFSET :offset
        """.format(filterstr, order_by_clause))

    filter_data["limit"] = kwargs.pop("limit", None)
    filter_data["offset"] = kwargs.pop("offset", None)

    if kwargs:
        raise TypeError('Unexpected **kwargs: %r' % kwargs)

    with db.engine.connect() as connection:
        results = connection.execute(query, filter_data)
        rows = results.fetchall()
        rows = [dict(row) for row in rows]
        # Orgainze last revision info in reviews
        if rows:
            for row in rows:
                row["last_revision"] = {
                    "id": row.pop("latest_revision_id"),
                    "timestamp": row.pop("latest_revision_timestamp"),
                    "text": row["text"],
                    "review_id": row["id"],
                }
                row["user"] = User({
                    "id": row["user_id"],
                    "display_name": row.pop("display_name"),
                    "show_gravatar": row.pop("show_gravatar"),
                    "is_blocked": row.pop("is_blocked"),
                    "musicbrainz_username": row.pop("musicbrainz_id"),
                    "email": row.pop("email"),
                    "created": row.pop("user_created"),
                })
    return rows, count


def get_popular(limit=None):
    """Get list of popular reviews.

    Popularity is determined by rating of a particular review. Rating is a difference between
    positive votes and negative. In this case only votes from the last month are
    used to calculate rating.

    Results are cached for 1 hour.

    Args:
        limit: Maximum number of reviews to return.

    Returns:
        Randomized list of popular reviews which are converted into dictionaries using to_dict method.
    """
    cache_key = cache.gen_key('popular_reviews', limit)
    reviews = cache.get(cache_key, REVIEW_CACHE_NAMESPACE)
    reviews = None
    defined_limit = 4 * limit if limit else None

    if not reviews:
        with db.engine.connect() as connection:
            results = connection.execute(sqlalchemy.text("""
                SELECT review.id,
                       entity_id,
                       entity_type,
                       review.user_id,
                       edits,
                       is_draft,
                       is_hidden,
                       license_id,
                       language,
                       source,
                       source_url,
                       SUM(
                        CASE
                          WHEN vote = 't' THEN 1
                          WHEN vote = 'f' THEN -1
                          WHEN vote IS NULL THEN 0
                        END
                       ) AS rating,
                       latest_revision.id AS latest_revision_id,
                       latest_revision.timestamp AS latest_revision_timestamp,
                       latest_revision.text AS text
                      FROM review
                  JOIN revision
                    ON revision.review_id = review.id
             LEFT JOIN vote
                    ON vote.revision_id = revision.id
                  JOIN (
                        revision
                        JOIN (
                          SELECT review.id AS review_uuid,
                                 MAX(timestamp) AS latest_timestamp
                            FROM review
                            JOIN revision
                              ON review.id = review_id
                        GROUP BY review.id
                             ) AS latest
                          ON latest.review_uuid = revision.review_id
                         AND latest.latest_timestamp = revision.timestamp
                       ) AS latest_revision
                    ON review.id = latest_revision.review_id
                 WHERE entity_id
                    IN (
                          SELECT
                        DISTINCT entity_id
                            FROM (
                          SELECT entity_id
                            FROM review
                        ORDER BY RANDOM()
                        ) AS randomized_entity_ids
                       )
              GROUP BY review.id, latest_revision.id
              ORDER BY rating
                 LIMIT :limit
            """), {
                "limit": defined_limit,
            })
            reviews = results.fetchall()

        reviews = [dict(review) for review in reviews]
        if reviews:
            for review in reviews:
                review["last_revision"] = {
                    "id": review.pop("latest_revision_id"),
                    "timestamp": review.pop("latest_revision_timestamp"),
                    "text": review["text"],
                    "review_id": review["id"],
                }
            reviews = [to_dict(review, confidential=True) for review in reviews]

        cache.set(cache_key, reviews, 1 * 60 * 60, REVIEW_CACHE_NAMESPACE) # 1 hour
    shuffle(reviews)
    return reviews[:limit]


def delete(review_id):
    """Delete a review, given the review ID.

    Args:
        review_id: ID of the review to be deleted.
    """
    with db.engine.connect() as connection:
        connection.execute(sqlalchemy.text("""
            DELETE
              FROM review
             WHERE id = :review_id
        """), {
            "review_id": review_id,
        })
