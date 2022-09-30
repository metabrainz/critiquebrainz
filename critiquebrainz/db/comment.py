# critiquebrainz - Repository for Creative Commons licensed reviews
#
# Copyright (C) 2018 MetaBrainz Foundation Inc.
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

import sqlalchemy

import critiquebrainz.db as db
import critiquebrainz.db.comment_revision as db_comment_revision
import critiquebrainz.db.exceptions as db_exceptions
from critiquebrainz.db.user import User


def create(*, user_id, text, review_id, is_draft=False):
    """Create a new comment.

    Args:
        user_id (uuid): the ID of the user
        text (str): the text of the comment
        review_id (uuid): the ID of the review
        is_draft (bool): a flag specifying whether the comment is a draft

    Returns:
        the newly created comment in dict form
    """
    with db.engine.connect() as connection:
        result = connection.execute(sqlalchemy.text("""
            INSERT INTO comment (user_id, review_id, is_draft)
                 VALUES (:user_id, :review_id, :is_draft)
              RETURNING id
            """), {
                'user_id': user_id,
                'review_id': review_id,
                'is_draft': is_draft,
                })
        comment_id = result.fetchone()['id']
        db_comment_revision.create(comment_id, text)
    return get_by_id(comment_id)


def get_by_id(comment_id):
    """ Get a comment by its ID.

    Args:
        comment_id (uuid): the ID of the comment

    Returns:
        dict representing the comment. The dict has the following structure:

        {
            'id',
            'review_id',
            'user_id',
            'edits',
            'is_hidden',
            'last_revision': {
                'id',
                'timestamp',
                'text'
            },
            'user',
        }
    """
    with db.engine.connect() as connection:
        result = connection.execute(sqlalchemy.text("""
            SELECT c.id,
                   c.review_id,
                   c.user_id,
                   c.edits,
                   c.is_hidden,
                   cr.id as last_revision_id,
                   cr.timestamp,
                   cr.text,
                   "user".email,
                   "user".created as user_created,
                   "user".display_name,
                   "user".musicbrainz_id,
                   COALESCE("user".musicbrainz_id, "user".id::text) as user_ref,
                   "user".is_blocked
              FROM comment c
              JOIN comment_revision cr ON c.id = cr.comment_id
              JOIN "user" ON c.user_id = "user".id
             WHERE c.id = :comment_id
          ORDER BY cr.timestamp DESC
             LIMIT 1
            """), {
                'comment_id': comment_id,
                })

        comment = result.fetchone()
        if not comment:
            raise db_exceptions.NoDataFoundException('Can\'t find comment with ID: {id}'.format(id=comment_id))

        comment = dict(comment)
        comment['last_revision'] = {
            'id': comment.pop('last_revision_id'),
            'timestamp': comment.pop('timestamp'),
            'text': comment.pop('text'),
        }
        comment['user'] = User({
            'id': comment['user_id'],
            'display_name': comment.pop('display_name'),
            'email': comment.pop('email'),
            'created': comment.pop('user_created'),
            'musicbrainz_username': comment.pop('musicbrainz_id'),
            'user_ref': comment.pop('user_ref'),
            'is_blocked': comment.pop('is_blocked')
        })
        return comment


def list_comments(*, review_id=None, user_id=None, limit=20, offset=0, inc_hidden=False):
    """ Returns a list of comments according the specified filters.

    Args:
        review_id: the ID of the review for which comments are to be listed,
        user_id: the ID of the user for whom comments are to be listed,
        limit : Maximum number of comments to return.
        offset: Offset that can be used in conjunction with the limit.
        inc_hidden: whether to include hidden comments or not.

    Returns:
        (comments, comment_count)
        where comments is list of dicts, each dict representing a comment
              comment_count is an integer representing number of comments returned
    """
    filters = []
    query_vals = {}
    if review_id:
        filters.append('comment.review_id = :review_id')
        query_vals['review_id'] = review_id

    if inc_hidden:
        filters.append('commend.is_hidden = :is_hidden')
        query_vals['is_hidden'] = inc_hidden

    if user_id:
        filters.append('comment.user_id = :user_id')
        query_vals['user_id'] = user_id

    filterstr = ''
    if filters:
        filterstr = 'WHERE {condition}'.format(condition='AND'.join(filters))

    query_vals['limit'] = limit
    query_vals['offset'] = offset

    with db.engine.connect() as connection:
        result = connection.execute(sqlalchemy.text("""
            SELECT comment.id,
                   comment.review_id,
                   comment.user_id,
                   comment.edits,
                   comment.is_hidden,
                   "user".email,
                   "user".created as user_created,
                   "user".display_name,
                   "user".musicbrainz_id,
                   COALESCE("user".musicbrainz_id, "user".id::text) as user_ref,
                   "user".is_blocked,
                   MIN(comment_revision.timestamp) as created,
                   latest_revision.id as last_revision_id,
                   latest_revision.timestamp as last_revision_timestamp,
                   latest_revision.text as text
              FROM comment
              JOIN comment_revision ON comment.id = comment_revision.comment_id
              JOIN review ON comment.review_id = review.id
              JOIN "user" ON comment.user_id = "user".id
              JOIN (
                    comment_revision
                    JOIN (
                            SELECT comment.id as comment_uuid,
                                   MAX(timestamp) as latest_timestamp
                              FROM comment
                              JOIN comment_revision
                                ON comment.id = comment_revision.comment_id
                          GROUP BY comment.id
                         ) AS latest
                    ON comment_revision.comment_id = latest.comment_uuid
                   AND comment_revision.timestamp = latest.latest_timestamp
                   ) AS latest_revision ON comment.id = latest_revision.comment_uuid
              {where_clause}
          GROUP BY comment.id, latest_revision.id, "user".id
          ORDER BY created
             LIMIT :limit
            OFFSET :offset
            """.format(where_clause=filterstr)), query_vals)

        rows = [dict(row) for row in result.fetchall()]
        for row in rows:
            row['last_revision'] = {
                'id': row.pop('last_revision_id'),
                'timestamp': row.pop('last_revision_timestamp'),
                'text': row.pop('text')
            }
            row['user'] = User({
                'id': row['user_id'],
                'display_name': row.pop('display_name'),
                'is_blocked': row.pop('is_blocked'),
                'musicbrainz_username': row.pop('musicbrainz_id'),
                'user_ref': row.pop('user_ref'),
                'email': row.pop('email'),
                'created': row.pop('user_created'),
            })

    return rows, len(rows)


def delete(comment_id):
    """ Delete the comment with the specified ID.

    Args:
        comment_id (uuid): the ID of the comment to be deleted.
    """
    with db.engine.connect() as connection:
        connection.execute(sqlalchemy.text("""
            DELETE
              FROM comment
             WHERE id = :comment_id
            """), {
                'comment_id': comment_id,
                })


def update(comment_id, *, text=None, is_draft=None, is_hidden=None):
    """ Update the comment with the specified ID.

    Args:
        comment_id (uuid): the ID of the comment to be updated.
        text (str): the new text of the comment
        is_draft (bool): whether the comment is a draft or not
        is_hidden (bool): whether the comment is hidden or not
    """
    if text is None and is_draft is None and is_hidden is None:
        return

    comment = get_by_id(comment_id)

    updates = []
    update_data = {}
    if is_draft is not None:
        if not comment['is_draft'] and is_draft:
            raise Exception
        updates.append('is_draft = :is_draft')
        update_data['is_draft'] = is_draft

    if is_hidden is not None:
        updates.append('is_hidden = :is_hidden')
        update_data['is_hidden'] = is_hidden

    updates.append('edits = :edits')
    update_data['edits'] = comment['edits'] + 1

    setstr = ', '.join(updates)
    update_data['comment_id'] = comment_id
    with db.engine.connect() as connection:
        connection.execute(sqlalchemy.text("""
                UPDATE comment
                   SET {setstr}
                 WHERE id = :comment_id
            """.format(setstr=setstr)), update_data)

    if text is not None:
        db_comment_revision.create(comment_id, text)


def count_comments(*, review_id=None, user_id=None, is_hidden=None, is_draft=None):
    """ Returns the number of comments that satisfy provided filters.

    Args:
        review_id: the ID of the review for which comments are to be counted.
        user_id: the ID of the user whose comments are to be counted.
        is_hidden: flag to specify whether to count hidden or non-hidden comments
        is_draft: flag to specify whether to count drafts or published comments.

    Returns:
        (int): the number of comments that satisfy provided filters.
    """
    filters = []
    filter_data = {}
    if review_id:
        filters.append('review_id = :review_id')
        filter_data['review_id'] = review_id

    if user_id:
        filters.append('user_id = :user_id')
        filter_data['user_id'] = user_id

    if is_hidden is not None:
        filters.append('is_hidden = :is_hidden')
        filter_data['is_hidden'] = is_hidden

    if is_draft is not None:
        filters.append('is_draft = :is_draft')
        filter_data['is_draft'] = is_draft

    filterstr = ''
    if filters:
        filterstr = 'WHERE {conditions}'.format(conditions=' AND '.join(filters))

    with db.engine.connect() as connection:
        result = connection.execute(sqlalchemy.text("""
            SELECT COUNT(*)
              FROM comment
            {where_condition}
            """.format(where_condition=filterstr)), filter_data)
        return result.fetchone()[0]
