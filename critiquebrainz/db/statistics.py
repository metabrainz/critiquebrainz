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

from datetime import date
import sqlalchemy
from brainzutils import cache
from critiquebrainz import db
import critiquebrainz.db.exceptions as db_exceptions

_CACHE_NAMESPACE = "cb_statistics"
_DEFAULT_CACHE_EXPIRATION = 1 * 60 * 60  # seconds (1 hour)


def get_top_users(from_date=date(1970, 1, 1), to_date=date.today(), review_weight=1,
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
    with db.engine.connect() as connection:
        result = connection.execute(sqlalchemy.text("""
            WITH score_table AS (
                 SELECT id,
                        display_name,
                        COALESCE(rc, 0) AS review_count,
                        COALESCE(cc, 0) AS comment_count,
                        COALESCE(vc, 0) AS vote_count,
                        (
                            COALESCE(rc, 0)*:review_weight +
                            COALESCE(cc, 0)*:comment_weight +
                            COALESCE(vc, 0)*:vote_weight
                        ) AS score
                   FROM "user"
              LEFT JOIN (
                         SELECT user_id,
                                count(*) AS rc
                           FROM review
                      LEFT JOIN (
                                 SELECT review_id,
                                        min(timestamp) AS reviewed_at
                                   FROM revision
                               GROUP BY review_id
                                ) AS review_create
                             ON review.id = review_create.review_id
                          WHERE reviewed_at >= :from_date AND reviewed_at <= :to_date
                            AND review.is_draft = 'f'
                            AND review.is_hidden = 'f'
                       GROUP BY user_id
                        ) AS num_review
                     ON "user".id = num_review.user_id
              LEFT JOIN (
                         SELECT user_id,
                                count(*) AS cc
                           FROM comment
                      LEFT JOIN (
                                 SELECT comment_id,
                                        min(timestamp) AS commented_at
                                   FROM comment_revision
                               GROUP BY comment_id
                                ) AS comment_create
                             ON comment.id = comment_create.comment_id
                          WHERE commented_at >= :from_date AND commented_at <= :to_date
                            AND comment.is_draft = 'f'
                            AND comment.is_hidden = 'f'
                       GROUP BY user_id
                                ) AS num_comment
                     ON "user".id = num_comment.user_id
              LEFT JOIN (
                         SELECT user_id,
                                count(*) AS vc
                           FROM (
                                 SELECT user_id
                                   FROM vote
                                  WHERE rated_at >= :from_date AND rated_at <= :to_date
                                ) AS vote_before
                       GROUP BY user_id
                        ) AS num_vote
                     ON "user".id = num_vote.user_id
            ) SELECT * FROM score_table
                      WHERE score != 0
                   ORDER BY score DESC
                      LIMIT :limit
        """), {
            "from_date": from_date,
            "to_date": to_date,
            "review_weight": review_weight,
            "comment_weight": comment_weight,
            "vote_weight": vote_weight,
            "limit": limit,
        })

        top_scorers = result.fetchall()
        if not top_scorers:
            raise db_exceptions.NoDataFoundException("Can't get top users!")
        rows = [dict(row) for row in top_scorers]
        return rows


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

            for user in results:
                user["id"] = str(user["id"])

            top_users = {
                "users": results,
            }

            cache.set(key=key, val=top_users, namespace=_CACHE_NAMESPACE, time=_DEFAULT_CACHE_EXPIRATION)
        except db_exceptions.NoDataFoundException:
            return None
    return top_users["users"]
