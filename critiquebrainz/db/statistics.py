# critiquebrainz - Repository for Creative Commons licensed reviews
#
# Copyright (C) 2019 Bimalkant Lauhny.
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License along
# with this program; if not, write to the Free Software Foundation, Inc.,
# 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301 USA.

from datetime import date, timedelta

import sqlalchemy
from brainzutils import cache

import critiquebrainz.db.exceptions as db_exceptions
from critiquebrainz import db

_CACHE_NAMESPACE = "cb_statistics"
_DEFAULT_CACHE_EXPIRATION = 1 * 60 * 60  # seconds (1 hour)


def merge_rows(list_1, list_2, key):
    """ Merges two lists of dicts based on key in dicts

    Args:
        list_1(list[dict(),]): A list of dictionaries
        list_2(list[dict(),]): A list of dictionaries
        key(string): key using which lists would be merged

    Returns:
        List of dictionaries updated after merging two lists
    """

    merged = dict()
    for row in list_1 + list_2:
        if row[key] in merged:
            merged[row[key]].update(row)
        else:
            merged[row[key]] = row
    return list(merged.values())


def get_users_with_review_count(from_date=date(1970, 1, 1), to_date=date.today() + timedelta(1)):
    """ Gets list of users with number of reviews they've submitted

    Args:
        from_date(datetime): Date from which contributions by users are to be considered.
        to_date(datetime): Date upto which contributions by users are to be considered.

    Returns:
        List of dictionaries where each dictionary has the following structure:
        {
            "id": (uuid),
            "display_name": (str),
            "review_count": (int),
        }
    """
    with db.engine.connect() as connection:
        result = connection.execute(sqlalchemy.text("""
            SELECT id,
                   display_name,
                   COALESCE(rc, 0) AS review_count
              FROM "user"
         LEFT JOIN (SELECT user_id,
                           count(*) AS rc
                      FROM review
                     WHERE published_on >= :from_date AND published_on <= :to_date
                       AND review.is_draft = 'f'
                       AND review.is_hidden = 'f'
                  GROUP BY user_id) AS num_review
                ON "user".id = num_review.user_id
        """), {
            "from_date": from_date,
            "to_date": to_date,
        })

        reviewers = result.fetchall()
        if not reviewers:
            raise db_exceptions.NoDataFoundException("Can't get users with review count!")
        reviewers = [dict(reviewer) for reviewer in reviewers]
        return reviewers


def get_users_with_vote_count(from_date=date(1970, 1, 1), to_date=date.today() + timedelta(1)):
    """ Gets list of users with number of votes they've submitted

    Args:
        from_date(datetime): Date from which contributions by users are to be considered.
        to_date(datetime): Date upto which contributions by users are to be considered.

    Returns:
        List of dictionaries where each dictionary has the following structure:
        {
            "id": (uuid),
            "display_name": (str),
            "vote_count": (int),
        }
    """
    with db.engine.connect() as connection:
        result = connection.execute(sqlalchemy.text("""
            SELECT id,
                   display_name,
                   COALESCE(vc, 0) AS vote_count
              FROM "user"
         LEFT JOIN (SELECT user_id,
                           count(*) AS vc
                      FROM vote
                     WHERE rated_at >= :from_date AND rated_at <= :to_date
                  GROUP BY user_id) AS num_votes
                ON "user".id = num_votes.user_id
        """), {
            "from_date": from_date,
            "to_date": to_date,
        })

        voters = result.fetchall()
        if not voters:
            raise db_exceptions.NoDataFoundException("Can't get users with vote count!")
        voters = [dict(voter) for voter in voters]
        return voters


def get_users_with_comment_count(from_date=date(1970, 1, 1), to_date=date.today() + timedelta(1)):
    """ Gets list of users with number of comments they've submitted

    Args:
        from_date(datetime): Date from which contributions by users are to be considered.
        to_date(datetime): Date upto which contributions by users are to be considered.

    Returns:
        List of dictionaries where each dictionary has the following structure:
        {
            "id": (uuid),
            "display_name": (str),
            "comment_count": (int),
        }
    """
    with db.engine.connect() as connection:
        result = connection.execute(sqlalchemy.text("""
            SELECT id,
                   display_name,
                   COALESCE(cc, 0) AS comment_count
              FROM "user"
         LEFT JOIN (SELECT user_id,
                           count(*) AS cc
                      FROM comment
                 LEFT JOIN (SELECT comment_id,
                                   min(timestamp) AS commented_at
                              FROM comment_revision
                          GROUP BY comment_id) AS comment_create
                        ON comment.id = comment_create.comment_id
                     WHERE commented_at >= :from_date AND commented_at <= :to_date
                  GROUP BY user_id) AS num_comment
                ON "user".id = num_comment.user_id
        """), {
            "from_date": from_date,
            "to_date": to_date,
        })

        commenters = result.fetchall()
        if not commenters:
            raise db_exceptions.NoDataFoundException("Can't get users with comment count!")
        commenters = [dict(commenter) for commenter in commenters]
        return commenters


def get_top_users(from_date=date(1970, 1, 1), to_date=date.today() + timedelta(1), review_weight=1,
                  comment_weight=1, vote_weight=1, limit=10):
    """ Gets list of top contributors based on number of reviews, votes and comments
        along with their final scores.
        score = (reviews * review_weight + comments * comment_weight + votes * vote_weight)
        Results are sorted in ascending order by score and max number of results are
        defined by 'limit'.

    Args:
        from_date(datetime): Date from which contributions by users are to be considered.
        to_date(datetime): Date upto which contributions by users are to be considered.
        review_weight(int): Weight for each review of a user to add to their final score
        comment_weight(int): Weight for each comment of a user to add to their final score
        vote_weight(int): Weight for each vote of a user to add to their final score

    Returns:
        List of dictionaries where each dictionary has the following structure:
        {
            "id": (uuid),
            "display_name": (str),
            "review_count": (int),
            "comment_count": (int),
            "vote_count": (int),
            "score": (int),
        }
    """

    reviewers = get_users_with_review_count(from_date=from_date, to_date=to_date)
    commenters = get_users_with_comment_count(from_date=from_date, to_date=to_date)
    voters = get_users_with_vote_count(from_date=from_date, to_date=to_date)

    # merge based on user_id
    top_scorers = merge_rows(merge_rows(reviewers, commenters, "id"), voters, "id")

    # add 'score' for each user
    for user in top_scorers:
        user["id"] = str(user["id"])
        user["score"] = user["review_count"] * review_weight + user["comment_count"] * comment_weight + user[
            "vote_count"] * vote_weight

    # sort top_users by 'score' in descending order and keep only top 'limit' users
    top_scorers = sorted(top_scorers, key=lambda row: row["score"], reverse=True)[:limit]
    if top_scorers[0]["score"] == 0:
        top_scorers = []
    return top_scorers


def get_top_users_overall():
    """ Gets top contributors since the beginning

    Returns:
        Returns:
        List of dictionaries where each dictionary has the following structure:
        {
            "id": (str),
            "display_name": (str),
            "review_count": (int),
            "comment_count": (int),
            "vote_count": (int),
            "score": (int),
        }
    """
    key = cache.gen_key("top_users_overall", _CACHE_NAMESPACE)
    top_users = cache.get(key, _CACHE_NAMESPACE)

    # if could not fetch results from cache, or fetched results have to be updated
    if not top_users:

        try:
            results = get_top_users(
                review_weight=5,
                comment_weight=2,
                vote_weight=1,
            )

            top_users = {
                "users": results,
            }

            cache.set(key=key, val=top_users, namespace=_CACHE_NAMESPACE, time=_DEFAULT_CACHE_EXPIRATION)
        except db_exceptions.NoDataFoundException:
            return None
    return top_users["users"]
