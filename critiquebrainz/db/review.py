import uuid
from datetime import datetime, timedelta
from random import shuffle
from typing import List

import pycountry
import sqlalchemy
from brainzutils import cache
from flask import current_app
from flask_babel import lazy_gettext

from critiquebrainz import db
from critiquebrainz.db import (exceptions as db_exceptions,
                               revision as db_revision,
                               users as db_users,
                               avg_rating as db_avg_rating,
                               RATING_SCALE_1_5)
from critiquebrainz.db.user import User

REVIEW_CACHE_NAMESPACE = "Review"
DEFAULT_LICENSE_ID = "CC BY-SA 3.0"
DEFAULT_LANG = "en"

#: list of allowed entity_type's for writing/querying a review
MUSICBRAINZ_ENTITY_TYPES = {
    "event": lazy_gettext("Event"),
    "place": lazy_gettext("Place"),
    "release_group": lazy_gettext("Release Group"),
    "work": lazy_gettext("Work"),
    "artist": lazy_gettext("Artist"),
    "label": lazy_gettext("Label"),
    "recording": lazy_gettext("Recording"),
}

BOOKBRAINZ_ENTITY_TYPES = {
    "bb_edition_group": lazy_gettext("Edition Group"),
    "bb_literary_work": lazy_gettext("Literary Work"),
    "bb_author": lazy_gettext("Author"),
    "bb_series": lazy_gettext("Series"),
}

ENTITY_TYPES_MAPPING = {**MUSICBRAINZ_ENTITY_TYPES, **BOOKBRAINZ_ENTITY_TYPES}
ENTITY_TYPES = list(ENTITY_TYPES_MAPPING.keys())

supported_languages = []
for lang in list(pycountry.languages):
    if 'iso639_1_code' in dir(lang):
        supported_languages.append(lang.iso639_1_code)


# TODO(code-master5): Rename this function. It doesn't convert a review to dictionary.
# Review that is passed to it is already a dictionary.
def to_dict(review, confidential=False, connection=None):
    if connection is not None:
        review["user"] = User(db_users.get_user_by_id(connection, review.pop("user_id")))
    else:
        review["user"] = User(db_users.get_by_id(review.pop("user_id")))
    review["user"] = review["user"].to_dict(confidential=confidential)
    review["id"] = str(review["id"])
    review["entity_id"] = str(review["entity_id"])
    review["last_updated"] = review["last_revision"]["timestamp"]
    review["last_revision"]["review_id"] = str(review["last_revision"]["review_id"])
    return review


def get_by_id(review_id: uuid.UUID):
    """Get a review by its ID.

    Args:
        review_id: ID of the review.

    Returns:
        Dictionary with the following structure
        {
            "id": uuid,
            "entity_id": uuid,
            "entity_type": str,
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
            "popularity": int,
            "rating": int,
            "text": str,
            "license": dict,
            "published_on": datetime,
        }
    """
    reviews = get_by_ids([review_id])
    if len(reviews) == 0:
        raise db_exceptions.NoDataFoundException(f"Can't find any reviews for the supplied IDs: {review_id}")
    return reviews[0]


def get_by_ids(review_ids: List[uuid.UUID]):
    """Get a list of reviews by their IDs.

    Args:
        review_ids: ID's of the reviews.

    Returns:
        List of dictionary with each having the following structure
        {
            "id": uuid,
            "entity_id": uuid,
            "entity_type": str,
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
            "popularity": int,
            "rating": int,
            "text": str,
            "license": dict,
            "published_on": datetime,
        }
    """
    with db.engine.connect() as connection:
        result = connection.execute(sqlalchemy.text("""
            SELECT review.id AS id,
                   review.entity_id,
                   review.entity_type,
                   review.user_id,
                   review.edits,
                   review.is_draft,
                   review.is_hidden,
                   review.license_id,
                   review.language,
                   review.source,
                   review.source_url,
                   review.published_on,
                   revision.id AS last_revision_id,
                   revision.timestamp,
                   revision.text,
                   revision.rating,
                   "user".email,
                   "user".created as user_created,
                   "user".display_name,
                   "user".musicbrainz_id,
                   COALESCE("user".musicbrainz_id, "user".id::text) as user_ref,
                   "user".is_blocked,
                   license.full_name,
                   license.info_url
              FROM review
              JOIN revision ON revision.review_id = review.id
              JOIN "user" ON "user".id = review.user_id
              JOIN license ON license.id = license_id
             WHERE review.id IN :review_ids
          ORDER BY timestamp DESC
        """), {
            "review_ids": tuple(map(str, review_ids)),
        })

        reviews = result.mappings().fetchall()

    results = []
    for review in reviews:
        review = dict(review)
        review["rating"] = RATING_SCALE_1_5.get(review["rating"])
        review["last_revision"] = {
            "id": review.pop("last_revision_id"),
            "timestamp": review.pop("timestamp"),
            "text": review.get("text"),
            "rating": review.get("rating"),
            "review_id": review.get("id"),
        }
        review["user"] = User({
            "id": review["user_id"],
            "display_name": review.pop("display_name", None),
            "is_blocked": review.pop("is_blocked", False),
            "musicbrainz_username": review.pop("musicbrainz_id"),
            "user_ref": review.pop("user_ref"),
            "email": review.pop("email"),
            "created": review.pop("user_created"),
        })
        review["license"] = {
            "id": review["license_id"],
            "info_url": review["info_url"],
            "full_name": review["full_name"],
        }
        votes = db_revision.votes(review["last_revision"]["id"])
        review["votes"] = {
            "positive": votes["positive"],
            "negative": votes["negative"],
        }
        review["popularity"] = review["votes"]["positive"] - review["votes"]["negative"]
        results.append(review)
    return results


def set_hidden_state(review_id, *, is_hidden):
    """Hide or reveal a review.

    Args:
        review_id (uuid): ID of the review the state of which needs to be changed.
        is_hidden (bool): True if review has to be hidden, False if not.
    """
    review = get_by_id(review_id)
    with db.engine.begin() as connection:
        connection.execute(sqlalchemy.text("""
            UPDATE review
               SET is_hidden = :is_hidden
             WHERE id = :review_id
        """), {
            "review_id": review_id,
            "is_hidden": is_hidden,
        })

    # update the average rating
    if review["rating"] is not None:
        db_avg_rating.update(review["entity_id"], review["entity_type"])


def get_count(*, is_draft=False, is_hidden=False):
    """Get the total number of reviews in CritiqueBrainz.

    Args:
        is_draft (bool): True if drafted reviews are to be counted.
        is_hidden (bool): True if hidden reviews are to be counted.
    """
    with db.engine.connect() as connection:
        result = connection.execute(sqlalchemy.text("""
            SELECT count(*)
              FROM review
             WHERE is_draft = :is_drafted
               AND is_hidden = :is_hidden
        """), {
            "is_drafted": is_draft,
            "is_hidden": is_hidden,
        })
        return result.fetchone().count


def update(review_id, *, drafted, text=None, rating=None, license_id=None, language=None, is_draft=None):
    # TODO: Get rid of `drafted` argument. This information about review should be retrieved inside this function.
    """Update a review.

    Args:
        review_id (uuid): ID of the review.
        drafted (bool): Whether the review is currently set as a draft.
        license_id (str): ID of a license that needs to be associated with this review.
        is_draft (bool): Whether to publish review (False) or keep it as a draft (True).
        text (str): Updated text part of a review.
        rating (int): Updated rating part of a review.
    """
    if text is None and rating is None:
        raise db_exceptions.BadDataException("Text part and rating part of a review can not be None simultaneously")

    updates = []
    updated_info = {}

    if license_id is not None:
        if not drafted:  # If trying to convert published review into draft
            raise db_exceptions.BadDataException("Changing license of a published review is not allowed.")
        updates.append("license_id = :license_id")
        updated_info["license_id"] = license_id

    if language is not None:
        updates.append("language = :language")
        updated_info["language"] = language

    if is_draft is not None:
        if not drafted and is_draft:  # If trying to convert published review into draft
            raise db_exceptions.BadDataException("Converting published reviews back to drafts is not allowed.")
        if drafted and not is_draft:
            published_on = datetime.now()
            updates.append("published_on = :published_on")
            updated_info["published_on"] = published_on
        updates.append("is_draft = :is_draft")
        updated_info["is_draft"] = is_draft

    setstr = ", ".join(updates)
    query = sqlalchemy.text("""
        UPDATE review
           SET {setstr}
         WHERE id = :review_id
    """.format(setstr=setstr))

    with db.engine.begin() as connection:
        if setstr:
            updated_info["review_id"] = review_id
            connection.execute(query, updated_info)
        db_revision.create(connection, review_id, text, rating)

    db_revision.update_rating(review_id)

    with db.engine.begin() as connection:
        result = connection.execute(sqlalchemy.text("""
                    SELECT review.entity_id,
                           review.entity_type,
                           review.user_id
                      FROM review
                     WHERE review.id = :review_id
                """), {
            "review_id": review_id,
        })
        review = dict(result.mappings().first())
        invalidate_ws_entity_cache(review["entity_id"], review["entity_type"], review["user_id"])


def create(*, entity_id, entity_type, user_id, is_draft, text=None, rating=None,
           language=DEFAULT_LANG, license_id=DEFAULT_LICENSE_ID,
           source=None, source_url=None):
    """Create a new review.

    Optionally, if a review is being imported from external source which needs
    a reference, you can specify `source` and `source_url` arguments. This
    reference will accompany the review.

    Args:
        entity_id: ID of an entity that review is for.
        entity_type (str): Entity type associated with the `entity_id`.
        user_id (uuid): ID of the reviewer.
        is_draft (bool): Whether this review is a draft (not shown to public).
        text (str): Text part of the review.
        rating (int): Rating part of the review.
        language (str): Language code that indicates which language the review
                        is written in.
        license_id (str): ID of the license.
        source (str): Name of the source of the review.
        source_url (str): URL pointing to the source of the review.

    Returns:
        Dictionary with the following structure
        {
            "id": uuid,
            "entity_id": uuid,
            "entity_type": str,
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
            "popularity": int,
            "text": str,
            "rating": int,
            "license": dict,
            "published_on": datetime,
        }
    """
    if text is None and rating is None:
        raise db_exceptions.BadDataException("Text part and rating part of a review can not be None simultaneously")
    if language not in supported_languages:
        raise ValueError("Language: {} is not supported".format(language))
    if is_draft:
        published_on = None
    else:
        published_on = datetime.now()

    with db.engine.begin() as connection:
        result = connection.execute(sqlalchemy.text("""
            INSERT INTO review (id, entity_id, entity_type, user_id, edits, is_draft, is_hidden, license_id, language, source, source_url, published_on)
            VALUES (:id, :entity_id, :entity_type, :user_id, :edits, :is_draft, :is_hidden, :license_id, :language, :source, :source_url, :published_on)
         RETURNING id;
        """), {  # noqa: E501
            "id": str(uuid.uuid4()),
            "entity_id": entity_id,
            "entity_type": entity_type,
            "user_id": user_id,
            "edits": 0,
            "is_draft": is_draft,
            "is_hidden": False,
            "language": language,
            "license_id": license_id,
            "source": source,
            "source_url": source_url,
            "published_on": published_on,
        })
        review_id = result.fetchone()[0]
        db_revision.create(connection, review_id, text, rating)
    if rating:
        db_revision.update_rating(review_id)

    invalidate_ws_entity_cache(entity_id, entity_type, user_id)
    return get_by_id(review_id)


def invalidate_ws_entity_cache(entity_id, entity_type, user_id):
    cache_keys_for_entity_id_key = cache.gen_key('ws_cache', entity_id)
    cache_keys_to_delete = cache.smembers(cache_keys_for_entity_id_key, namespace=REVIEW_CACHE_NAMESPACE)
    if cache_keys_to_delete:
        cache.delete_many(cache_keys_to_delete, namespace=REVIEW_CACHE_NAMESPACE)
        cache.delete(cache_keys_for_entity_id_key, namespace=REVIEW_CACHE_NAMESPACE)

    cache_keys_for_no_entity_id_key = cache.gen_key('ws_cache', 'entity_id_absent')
    cache_keys_to_delete = cache.smembers(cache_keys_for_no_entity_id_key, namespace=REVIEW_CACHE_NAMESPACE)
    if cache_keys_to_delete:
        cache.delete_many(cache_keys_to_delete, namespace=REVIEW_CACHE_NAMESPACE)
        cache.delete(cache_keys_for_no_entity_id_key, namespace=REVIEW_CACHE_NAMESPACE)

    # Invalidate top and latest reviews caches
    cache_keys_to_delete = [
        cache.gen_key(f'entity_api_{entity_type}', entity_id, review_type, f"{sort_type}_reviews")
        for sort_type in ('popularity', 'published_on')
        for review_type in ('review', 'rating', None)
    ]
    cache.delete_many(cache_keys_to_delete, namespace=REVIEW_CACHE_NAMESPACE)

    user = db_users.get_by_id(user_id)
    if user and 'musicbrainz_username' in user.keys() and user['musicbrainz_username']:
        username = user["musicbrainz_username"]
        cache_key = cache.gen_key('entity_api', entity_id, entity_type, username, "user_review")
        cache.delete(cache_key, namespace=REVIEW_CACHE_NAMESPACE)


# pylint: disable=too-many-branches
def get_reviews_list(connection, *, inc_drafts=False, inc_hidden=False, entity_id=None,
                     entity_type=None, license_id=None, user_id=None, language=None,
                     exclude=None, sort=None, sort_order=None, limit=20, offset=None, review_type=None):
    """
        helper function for list_reviews() that extends support for execution within a transaction by directly receiving the
        connection object
    """
    filters = []
    filter_data = {}
    if not inc_drafts:
        filters.append("is_draft = :is_draft")
        filter_data["is_draft"] = False

    if not inc_hidden:
        filters.append("is_hidden = :is_hidden")
        filter_data["is_hidden"] = False

    # FILTERING
    if entity_id is not None:
        filters.append("entity_id = :entity_id")
        filter_data["entity_id"] = entity_id

    if entity_type is not None:
        if entity_type == 'musicbrainz':
            filters.append("entity_type in :entity_type")
            filter_data["entity_type"] = tuple(MUSICBRAINZ_ENTITY_TYPES.keys())
        elif entity_type == 'bookbrainz':
            filters.append("entity_type in :entity_type")
            filter_data["entity_type"] = tuple(BOOKBRAINZ_ENTITY_TYPES.keys())
        else:
            filters.append("entity_type = :entity_type")
            filter_data["entity_type"] = entity_type

    if license_id is not None:
        filters.append("license_id = :license_id")
        filter_data["license_id"] = license_id

    if user_id is not None:
        filters.append("review.user_id = :user_id")
        filter_data["user_id"] = user_id

    if review_type == 'rating':
        filters.append("latest_revision.rating is not NULL")

    if review_type == 'review':
        filters.append("latest_revision.text is not NULL")

    if exclude is not None:
        filters.append("review.id NOT IN :exclude")
        filter_data["exclude"] = tuple(exclude)

    if language is not None:
        filters.append("language = :language")
        filter_data["language"] = language

    filterstr = " AND ".join(filters)
    if filterstr:
        filterstr = " WHERE " + filterstr

    latest_revision_query = """
        JOIN (
            revision
            JOIN (
                SELECT review.id AS review_uuid,
                       MAX(timestamp) AS latest_timestamp
                  FROM review
                  JOIN revision ON review.id = review_id
              GROUP BY review.id
            ) AS latest
              ON latest.review_uuid = revision.review_id
             AND latest.latest_timestamp = revision.timestamp
            ) AS latest_revision
          ON review.id = latest_revision.review_id
    """

    query = sqlalchemy.text("""
        SELECT COUNT(*)
          FROM review
            {latest_revision_query}
            {filterstr}
        """.format(filterstr=filterstr, latest_revision_query=latest_revision_query))

    result = connection.execute(query, filter_data)
    count = result.fetchone()[0]
    order_by_clause = ""
    if not sort_order:
        sort_order = 'DESC'
    if sort_order.upper() not in ('ASC', 'DESC'):
        raise ValueError("sort_order must be ASC or DESC")

    if sort == "popularity":
        order_by_clause = """
            ORDER BY popularity {sort_order}
        """.format(sort_order=sort_order)
    elif sort == "published_on":
        order_by_clause = """
            ORDER BY review.published_on {sort_order}
        """.format(sort_order=sort_order)
    elif sort == "random":
        order_by_clause = """
            ORDER BY RANDOM()
        """
    # Note that all revisions' votes are considered in this popularity
    query = sqlalchemy.text("""
        SELECT review.id,
               review.entity_id,
               review.entity_type,
               review.edits,
               review.is_draft,
               review.is_hidden,
               review.license_id,
               review.language,
               review.source,
               review.source_url,
               review.user_id,
               "user".display_name,
               "user".is_blocked,
               "user".email,
               "user".created as user_created,
               "user".musicbrainz_id,
               COALESCE("user".musicbrainz_id, "user".id::text) as user_ref,
               review.published_on,
               MIN(revision.timestamp) as created,
               SUM(
                   CASE WHEN vote='t' THEN 1 ELSE 0 END
               ) AS votes_positive_count,
               SUM(
                   CASE WHEN vote='f' THEN 1 ELSE 0 END
               ) AS votes_negative_count,
               SUM(
                   CASE WHEN vote = 't' THEN 1
                   WHEN vote = 'f' THEN -1 WHEN vote IS NULL THEN 0 END
               ) AS popularity,
               latest_revision.id as latest_revision_id,
               latest_revision.timestamp as latest_revision_timestamp,
               latest_revision.text as text,
               latest_revision.rating as rating,
               license.full_name,
               license.info_url
          FROM review
          JOIN revision ON review.id = revision.review_id
     LEFT JOIN vote ON vote.revision_id = revision.id
          JOIN "user" ON review.user_id = "user".id
          JOIN license ON license.id = license_id
        {latest_revision_query}   
        {where_clause}
      GROUP BY review.id, latest_revision.id, "user".id, license.id
        {order_by_clause}
         LIMIT :limit
        OFFSET :offset
        """.format(where_clause=filterstr, order_by_clause=order_by_clause, latest_revision_query=latest_revision_query))

    filter_data["limit"] = limit
    filter_data["offset"] = offset

    results = connection.execute(query, filter_data)
    rows = results.mappings()
    rows = [dict(row) for row in rows]

    # Organise last revision info in reviews
    if rows:
        for row in rows:
            row["rating"] = RATING_SCALE_1_5.get(row["rating"])
            row["last_revision"] = {
                "id": row.pop("latest_revision_id"),
                "timestamp": row.pop("latest_revision_timestamp"),
                "text": row["text"],
                "rating": row["rating"],
                "review_id": row["id"],
            }
            row["user"] = User({
                "id": row["user_id"],
                "display_name": row.pop("display_name"),
                "is_blocked": row.pop("is_blocked"),
                "musicbrainz_username": row.pop("musicbrainz_id"),
                "user_ref": row.pop("user_ref"),
                "email": row.pop("email"),
                "created": row.pop("user_created"),
            })

    return rows, count


def list_reviews(*, inc_drafts=False, inc_hidden=False, entity_id=None, entity_type=None,
                 license_id=None, user_id=None, language=None, exclude=None,
                 sort=None, sort_order='DESC', limit=20, offset=None, review_type=None):
    """Get a list of reviews.

    This function provides several filters that can be used to select a subset of reviews.

    Args:
        entity_id (uuid): ID of the entity that has been reviewed.
        entity_type (str): Type of the entity that has been reviewed. Can be either one of the entities supported or 
                            "musicbrainz" (for reviews about MusicBrainz entities) or "bookbrainz" (for reviews about bookbrainz entities).
        user_id (uuid): ID of the author.
        sort (str): Order of the returned reviews. Can be either "popularity" (order by difference in +/- votes),
                    "published_on" (order by publish time) or "random" (order randomly).
        sort_order (str): Order of the returned reviews. Can be either "asc" or "desc".
        limit (int): Maximum number of reviews to return.
        offset (int): Offset that can be used in conjunction with the limit.
        language (str): Language code of reviews.
        license_id (str): License ID that reviews are associated with.
        inc_drafts (bool): True if reviews marked as drafts should be included, False if not.
        inc_hidden (bool): True if reviews marked as hidden should be included, False if not.
        exclude (list): List of reviews (their IDs) to exclude from results.
        review_type (str): Return reviews of this type. Can either be "review" (to return reviews with text),
                           or "rating" (to return reviews which have a rating), or ``None`` (to return all reviews).

    Returns:
        Tuple with two values:
        1. list of reviews as dictionaries,
        2. total number of reviews that match the specified filters.
    """
    with db.engine.connect() as connection:
        return get_reviews_list(connection, inc_drafts=inc_drafts, inc_hidden=inc_hidden, entity_id=entity_id,
                                entity_type=entity_type, license_id=license_id, user_id=user_id,
                                language=language, exclude=exclude, sort=sort, sort_order=sort_order, limit=limit, 
                                offset=offset, review_type=review_type)


def get_popular_reviews_for_index():
    """Get a list of popular reviews for displaying on the home page.

    popularity is a difference between positive votes and negative. In this
    case only votes from the last month are used to calculate popularity
    to make results more varied.

    Returns:
        Randomized list of popular reviews which are converted into
        dictionaries using to_dict method.
    """
    limit = current_app.config['POPULAR_REVIEWS_LIMIT']
    cache_key = cache.gen_key("popular_reviews", limit)
    reviews = cache.get(cache_key, REVIEW_CACHE_NAMESPACE)
    defined_limit = 4 * limit if limit else None
    reset_cache = any([check_review_deleted(review["id"]) for review in reviews]) if reviews else False

    if not reviews or reset_cache:
        with db.engine.connect() as connection:
            results = connection.execute(sqlalchemy.text("""
                SELECT review.id,
                       review.entity_id,
                       review.entity_type,
                       review.user_id,
                       review.edits,
                       review.is_draft,
                       review.is_hidden,
                       review.license_id,
                       review.language,
                       review.source,
                       review.source_url,
                       SUM(
                           CASE WHEN vote = 't' THEN 1
                                WHEN vote = 'f' THEN -1
                                WHEN vote IS NULL THEN 0 END
                       ) AS popularity,
                       latest_revision.id AS latest_revision_id,
                       latest_revision.timestamp AS latest_revision_timestamp,
                       latest_revision.text AS text,
                       latest_revision.rating AS rating
                  FROM review
                  JOIN revision ON revision.review_id = review.id
             LEFT JOIN (
                        SELECT revision_id, vote
                          FROM vote
                         WHERE rated_at > :last_month
                       ) AS votes_last_month
                    ON votes_last_month.revision_id = revision.id
                  JOIN (
                        revision JOIN (
                          SELECT review.id AS review_uuid,
                                 MAX(timestamp) AS latest_timestamp
                            FROM review
                            JOIN revision ON review.id = review_id
                        GROUP BY review.id
                        ) AS latest ON latest.review_uuid = revision.review_id
                        AND latest.latest_timestamp = revision.timestamp
                       ) AS latest_revision
                    ON review.id = latest_revision.review_id
                 WHERE entity_id
                    IN (
                        SELECT DISTINCT entity_id
                          FROM (
                        SELECT entity_id
                          FROM review
                      ORDER BY RANDOM()
                      ) AS randomized_entity_ids
                    )
                   AND latest_revision.text IS NOT NULL
                   AND review.is_hidden = 'f'
                   AND review.is_draft = 'f'
              GROUP BY review.id, latest_revision.id
              ORDER BY popularity
                 LIMIT :limit
            """), {
                "limit": defined_limit,
                "last_month": datetime.now() - timedelta(weeks=4)
            })
            reviews = [dict(review) for review in results.mappings()]

        if reviews:
            for review in reviews:
                review["rating"] = RATING_SCALE_1_5.get(review["rating"])
                review["last_revision"] = {
                    "id": review.pop("latest_revision_id"),
                    "timestamp": review.pop("latest_revision_timestamp"),
                    "text": review["text"],
                    "rating": review["rating"],
                    "review_id": review["id"],
                }
            reviews = [to_dict(review, confidential=False) for review in reviews]

        cache.set(cache_key, reviews, 1 * 60 * 60, namespace=REVIEW_CACHE_NAMESPACE)  # 1 hour
    shuffle(reviews)
    return reviews[:limit]


def delete(review_id):
    """Delete a review.

    Args:
        review_id: ID of the review to be deleted.
    """
    review = get_by_id(review_id)
    with db.engine.begin() as connection:
        connection.execute(sqlalchemy.text("""
            DELETE
              FROM review
             WHERE id = :review_id
        """), {
            "review_id": review_id,
        })

    if review["rating"] is not None:
        db_avg_rating.update(review["entity_id"], review["entity_type"])


def check_review_deleted(review_id) -> bool:
    """Check if a review exists in CB.

    Args:
        review_id: ID of the review to be checked.
    """
    with db.engine.connect() as connection:
        result = connection.execute(sqlalchemy.text("""
            SELECT NOT EXISTS (SELECT true FROM review WHERE id = :review_id) AS exists
        """), {
            "review_id": review_id,
        })

        return result.first().exists


def get_distinct_entities(connection):
    """
        helper function for distinct_entities() that extends support for execution within a transaction by directly receiving the
        connection object
    """
    query = sqlalchemy.text("""
        SELECT DISTINCT entity_id
          FROM review
    """)

    results = connection.execute(query)
    return {row["entity_id"] for row in results.mappings()}


def distinct_entities():
    """Get a set of ID(s) of entities reviewed.

    Returns:
        Set of ID(s) of distinct entities reviewed.
    """
    # TODO(roman): There's some room for improvement in the future since this
    # function assumes that IDs are unique between entity types. But it would
    # be better to remove that assumption before we support reviewing entities
    # from other sources (like BookBrainz).

    with db.engine.connect() as connection:
        return get_distinct_entities(connection)


def reviewed_entities(*, entity_ids, entity_type):
    """Check if an entity has been reviewed.

    Args:
        entity_ids: List of ID(s) of the entities.
        entity_type: Type of the entities.
    Returns:
        List of entity ID(s) that have a review in the database.
    """
    with db.engine.connect() as connection:
        results = connection.execute(sqlalchemy.text("""
            SELECT entity_id
              FROM review
             WHERE entity_type = :entity_type
               AND entity_id IN :entity_ids
        """), {
            "entity_type": entity_type,
            "entity_ids": tuple(entity_ids),
        })
        return [str(row["entity_id"]) for row in results.mappings()]
