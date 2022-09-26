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


def create(conn, comment_id, text):
    """ Create a new revision for comment with specified ID.

    Args:
        comment_id (uuid): the ID of the comment for which revision is to be created.
        text (str): the text of the new revision.

    Returns:
        int: the ID of the new revision created.
    """
    result = conn.execute(sqlalchemy.text("""
        INSERT INTO comment_revision (comment_id, text)
             VALUES (:comment_id, :text)
          RETURNING id
        """), {
            'comment_id': comment_id,
            'text': text,
            })

    return result.fetchone()['id']
