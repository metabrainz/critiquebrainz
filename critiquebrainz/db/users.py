import uuid
from datetime import datetime
from hashlib import md5

import sqlalchemy

from critiquebrainz import db
from critiquebrainz.db import revision as db_revision


USER_GET_COLUMNS = [
    'id',
    'display_name',
    'email',
    'created',
    'musicbrainz_id as musicbrainz_username',
    'musicbrainz_row_id',
    'license_choice',
    'is_blocked',
]


def get_many_by_mb_username(usernames):
    """Get information about users.

    Args:
        usernames (list): A list of MusicBrainz usernames. This lookup is case-insensetive.

    Returns:
        All columns of 'user' table (list of dictionaries).
        If the 'usernames' variable is an empty list function returns it back.
    """
    if not usernames:
        return []

    with db.engine.connect() as connection:
        result = connection.execute(sqlalchemy.text("""
            SELECT {columns}
              FROM "user"
             WHERE musicbrainz_id ILIKE ANY(:musicbrainz_usernames)
        """.format(columns=','.join(USER_GET_COLUMNS))), {
            'musicbrainz_usernames': usernames,
        })
        row = result.fetchall()
        users = [dict(r) for r in row]
        return users


def get_user_by_id(connection, user_id):
    """
        helper function for get_by_id() that extends support for execution within a transaction by directly receiving the
        connection object
    """
    query = sqlalchemy.text("""
        SELECT {columns}
          FROM "user"
         WHERE id = :user_id
    """.format(columns=','.join(USER_GET_COLUMNS)))

    result = connection.execute(query, {
        "user_id": user_id
    })
    row = result.fetchone()
    if not row:
        return None
    row = dict(row)
    return row


def get_by_id(user_id):
    """Get user from user_id (UUID).

    Args:
        user_id(uuid): ID of the user.

    Returns:
        Dictionary with the following structure:
        {
            "id": (uuid),
            "display_name": (str),
            "email": (str),
            "created": (datetime),
            "musicbrainz_username": (str),
            "is_blocked": (bool),
            "license_choice": (str)
        }
    """
    with db.engine.connect() as connection:
        return get_user_by_id(connection, user_id)


def create(**user_data):
    """Create user using the given details.

    Args:
        display_name(str): display_name of the user.
        musicbrainz_username(str, optional): musicbrainz username of user.
        musicbrainz_row_id (int): the MusicBrainz row ID of the user,
        email(str, optional): email of the user.
        is_blocked(bool, optional): whether user is blocked(default: false).
        license_choice(str, optional): preferred license for reviews by the user

    Returns:
        Dictionary with the following structure:
        {
            "id": (uuid),
            "display_name": (str),
            "email": (str),
            "created": (datetime),
            "musicbrainz_username": (str),
            "is_blocked": (bool),
            "license_choice": (str)
        }
    """
    display_name = user_data.pop('display_name')
    musicbrainz_username = user_data.pop('musicbrainz_username', None)
    email = user_data.pop('email', None)
    is_blocked = user_data.pop('is_blocked', False)
    license_choice = user_data.pop('license_choice', None)
    musicbrainz_row_id = user_data.pop('musicbrainz_row_id', None)
    if user_data:
        raise TypeError('Unexpected **user_data: %r' % user_data)

    with db.engine.connect() as connection:
        result = connection.execute(sqlalchemy.text("""
            INSERT INTO "user" (id, display_name, email, created, musicbrainz_id,
                                is_blocked, license_choice, musicbrainz_row_id)
                 VALUES (:id, :display_name, :email, :created, :musicbrainz_id,
                        :is_blocked, :license_choice, :musicbrainz_row_id)
              RETURNING id
        """), {
            "id": str(uuid.uuid4()),
            "display_name": display_name,
            "email": email,
            "created": datetime.now(),
            "musicbrainz_id": musicbrainz_username,
            "is_blocked": is_blocked,
            "license_choice": license_choice,
            "musicbrainz_row_id": musicbrainz_row_id,
        })
        new_id = result.fetchone()[0]
    return get_by_id(new_id)


def get_by_mbid(musicbrainz_username):
    """Get user by musicbrainz username.

    Args:
        musicbrainz_username(str): MusicBrainz username of the User.

    Returns:
        Dictionary with the following structure:
        {
            "id": (uuid),
            "display_name": (str),
            "email": (str),
            "created": (datetime),
            "musicbrainz_username": (str),
            "is_blocked": (bool),
            "license_choice": (str)
        }
    """
    with db.engine.connect() as connection:
        result = connection.execute(sqlalchemy.text("""
            SELECT {columns}
              FROM "user"
             WHERE musicbrainz_id = :musicbrainz_username
        """.format(columns=','.join(USER_GET_COLUMNS))), {
            "musicbrainz_username": musicbrainz_username,
        })
        row = result.fetchone()
        if not row:
            return None
        row = dict(row)
    return row


def get_or_create(musicbrainz_row_id, musicbrainz_username, new_user_data):
    """Get user from display_name and musicbrainz_username.

    Args:
        musicbrainz_row_id (int): the musicbrainz row ID of the user
        musicbrainz_username(str): MusicBrainz username of the user.
        new_user_data(dict): Dictionary containing the user data which may
                             contain the following keys:
        {
            "display_name": Display name of the user.
            "email": email of the user(optional).
            "is_blocked": whether user is blocked(default: false, optional).
            "license_choice": preferred license for reviews by the user(optional)
        }

    Returns:
        Dictionary with the following structure:
        {
            "id": (uuid),
            "display_name": (str),
            "email": (str),
            "created": (datetime),
            "musicbrainz_username": (str),
            "is_blocked": (bool),
            "license_choice": (str)
        }
    """
    user = get_by_mb_row_id(musicbrainz_row_id, musicbrainz_username)
    if not user:
        display_name = new_user_data.pop("display_name")
        user = create(
            musicbrainz_row_id=musicbrainz_row_id,
            display_name=display_name,
            musicbrainz_username=musicbrainz_username,
            **new_user_data
        )
    return user


def update_username(user, new_musicbrainz_id: str):
    """ Update the email field and MusicBrainz ID of the user specified by the lb_id

    Args:
        user: critiquebrainz user
        new_musicbrainz_id: MusicBrainz username of a user
    """
    # update display name only if the user has not changed it to something else than exising mb username
    update_display_name = user["musicbrainz_username"] == user["display_name"]

    updates = ["musicbrainz_id = :new_musicbrainz_id"]
    if update_display_name:
        updates.append("display_name = :new_musicbrainz_id")

    query = """
        UPDATE "user"
           SET {}
         WHERE id = :cb_id
    """.format(", ".join(updates))

    with db.engine.connect() as connection:
        connection.execute(sqlalchemy.text(query), {
            "cb_id": user["id"],
            "new_musicbrainz_id": new_musicbrainz_id,
        })

    user = dict(user)
    user["musicbrainz_username"] = new_musicbrainz_id
    if update_display_name:
        user["display_name"] = new_musicbrainz_id
    return user


def total_count():
    """Returns the total number of users of CritiqueBrainz.

    Returns:
        count: (int)
    """
    with db.engine.connect() as connection:
        result = connection.execute(sqlalchemy.text("""
            SELECT count(*)
              FROM "user"
        """))

        return result.fetchone()[0]


def list_users(limit=None, offset=0):
    """Returns the list of users of CritiqueBrainz.

    Args:
        limit(int, optional): Number of users to be returned.
        offset(int, optional): Number of initial users to skip.

    Returns:
        List of dictionaries of users with the following structure:
        {
            "id": (uuid),
            "display_name": (str),
            "email": (str),
            "created": (datetime),
            "musicbrainz_username": (str),
            "is_blocked": (bool),
            "license_choice": (str),
            "musicbrainz_row_id": (int),
        }
    """
    with db.engine.connect() as connection:
        result = connection.execute(sqlalchemy.text("""
            SELECT {columns}
              FROM "user"
             LIMIT :limit
            OFFSET :offset
        """.format(columns=','.join(USER_GET_COLUMNS))), {
            "limit": limit,
            "offset": offset
        })
        rows = result.fetchall()
        rows = [dict(row) for row in rows]
    return rows


def unblock(user_id):
    """Unblock user (admin only).

    Args:
        user_id(uuid): ID of user to be unblocked.
    """
    with db.engine.connect() as connection:
        connection.execute(sqlalchemy.text("""
            UPDATE "user"
               SET is_blocked = 'false'
             WHERE id = :user_id
        """), {
            "user_id": user_id
        })


def block(user_id):
    """Block user (admin only).

    Args:
        user_id(uuid): ID of user to be blocked.
    """
    with db.engine.connect() as connection:
        connection.execute(sqlalchemy.text("""
            UPDATE "user"
               SET is_blocked = 'true'
            WHERE id = :user_id
        """), {
            "user_id": user_id
        })


def has_voted(user_id, review_id):
    """Check if a user has already voted on the last revision of a review.

    Args:
        user_id(uuid): ID of the user.
        review_id(uuid): ID of the review.

    Returns:
        (bool): True if has voted else False.
    """
    last_revision = db_revision.get(review_id, limit=1)[0]
    with db.engine.connect() as connection:
        result = connection.execute(sqlalchemy.text("""
            SELECT count(*)
              FROM vote
             WHERE revision_id = :revision_id
               AND user_id = :user_id
        """), {
            "revision_id": last_revision['id'],
            "user_id": user_id
        })
        count = result.fetchone()[0]
    return count > 0


def karma(user_id):
    """Get the karma of a user.

    Args:
        user_id(uuid): ID of the user.

    Returns:
        karma_value(int): the karma of the user.
    """
    with db.engine.connect() as connection:
        result = connection.execute(sqlalchemy.text("""
            SELECT review.user_id, vote
              FROM ((vote
                     LEFT JOIN revision
                            ON revision.id = revision_id)
                     LEFT JOIN review
                            ON review.id = review_id)
         LEFT JOIN "user"
                ON "user".id = review.user_id
             WHERE "user".id = :user_id
        """), {
            "user_id": user_id
        })

        rows = result.fetchall()
        karma_value = 0
        for row in rows:
            if row.vote:  # positive
                karma_value += 1
            else:  # negative
                karma_value -= 1
    return karma_value


def reviews(user_id):
    """Get list of reviews written by a user.

    Args:
        user_id(uuid): ID of the user.

    Returns:
        List of reviews written by the user with the structure:
        {
            "id": (uuid),
            "entity_id": (uuid),
            "entity_type": event or place or release_group,
            "user_id": (uuid),
            "edits": (int),
            "is_draft": (bool),
            "license_id": (str),
            "language": (str),
            "source": (str),
            "source_url" (str)
        }
    """
    with db.engine.connect() as connection:
        result = connection.execute(sqlalchemy.text("""
            SELECT id,
                   entity_id,
                   entity_type,
                   user_id,
                   edits,
                   is_draft,
                   license_id,
                   language,
                   source,
                   source_url
              FROM review
             WHERE user_id = :user_id
        """), {
            "user_id": user_id
        })

        rows = result.fetchall()
    return [dict(row) for row in rows]


def get_votes(user_id, from_date=datetime.utcfromtimestamp(0)):
    """Get votes by a user from a specified time.

    Args:
        user_id(uuid): ID of the user.
        from_date(datetime): Date from which votes submitted by user are to be returned.

    Returns:
        List of votes submitted by the user from the time specified
        {
            "vote": (bool),
            "rated_at": (datetime)
        }
    """
    with db.engine.connect() as connection:
        result = connection.execute(sqlalchemy.text("""
            SELECT vote,
                   rated_at
              FROM vote
             WHERE user_id = :user_id
               AND rated_at >= :from_date
        """), {
            "user_id": user_id,
            "from_date": from_date
        })

        rows = result.fetchall()
    return [dict(row) for row in rows]


def get_reviews(user_id, from_date=datetime.utcfromtimestamp(0)):
    """Get reviews by a user from a specified time.

    Args:
        user_id(uuid): ID of the user.
        from_date(datetime): Date from which reviews submitted by user are to be returned.

    Returns:
        List of reviews by the user from the time specified
        {
            "id": (uuid),
            "entity_id": (uuid),
            "entity_type": event or place or release_group,
            "user_id": (uuid),
            "edits": (int),
            "is_draft": (bool),
            "license_id": (str),
            "language": (str),
            "source": (str),
            "source_url":(str),
        }
    """
    with db.engine.connect() as connection:
        result = connection.execute(sqlalchemy.text("""
            SELECT id,
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
                   creation_time
              FROM review
         LEFT JOIN (SELECT review_id,
                           min(timestamp) AS creation_time
                      FROM revision
                  GROUP BY review_id) AS review_create
                ON review.id = review_id
             WHERE user_id = :user_id
               AND creation_time > :from_date
        """), {
            "user_id": user_id,
            "from_date": from_date
        })

        rows = result.fetchall()
    return [dict(row) for row in rows]


def get_comments(user_id, from_date=datetime.utcfromtimestamp(0)):
    """Get comments on reviews by a user from a specified time.

    Args:
        user_id(uuid): ID of the user.
        from_date(datetime): Date from which comments on reviews submitted by user are to be returned.

    Returns:
        List of reviews by the user from the time specified
        {
            "id": (uuid),
            "review_id": (uuid),
            "user_id": (uuid),
            "edits": (int),
            "is_draft": (bool),
            "is_hidden": (bool),
            "creation_time": (str),
        }
    """
    with db.engine.connect() as connection:
        result = connection.execute(sqlalchemy.text("""
            SELECT id,
                   review_id,
                   user_id,
                   edits,
                   is_draft,
                   is_hidden,
                   creation_time
              FROM comment
         LEFT JOIN (SELECT comment_id,
                           min(timestamp) AS creation_time
                      FROM comment_revision
                  GROUP BY comment_id) AS comment_create
                ON comment.id = comment_id
             WHERE user_id = :user_id
               AND creation_time > :from_date
        """), {
            "user_id": user_id,
            "from_date": from_date
        })

        rows = result.fetchall()
    return [dict(row) for row in rows]


def update(user_id, user_new_info):
    """Update info of a user.

    Args:
        user_id: ID of user whose info is to be updated.
        user_new_info: Dictionary containing the new information for the user
        {
            "display_name": (str),
            "email": (str)
            "license_choice": (str)
        }
    """
    updates = []
    if "display_name" in user_new_info:
        updates.append("display_name = :display_name")
    if "email" in user_new_info:
        updates.append("email = :email")
    if "license_choice" in user_new_info:
        updates.append("license_choice = :license_choice")

    setstr = ", ".join(updates)
    query = sqlalchemy.text("""UPDATE "user"
                                  SET {}
                                WHERE id = :user_id
            """.format(setstr))
    if user_new_info:
        user_new_info["user_id"] = user_id
        with db.engine.connect() as connection:
            connection.execute(query, user_new_info)


def delete(user_id):
    """
    This function deletes user and all of the information associated with them.

    Args:
        user_id(uuid): ID of the user to be deleted.
    """
    with db.engine.connect() as connection:
        connection.execute(sqlalchemy.text("""
            DELETE
              FROM "user"
             WHERE id = :user_id
        """), {
            "user_id": user_id
        })


def clients(user_id):
    """Get list of oauth clients registered by user.

    Args:
        user_id(uuid): ID of the user.

    Returns:
        List of dictionaries of oauth clients of the user
        {
            "client_id": (unicode),
            "client_secret": (unicode),
            "redirect_uri": (unicode),
            "user_id": (uuid),
            "name": (unicode),
            "desc": (unicode),
            "website": (unicode)
        }
    """
    with db.engine.connect() as connection:
        result = connection.execute(sqlalchemy.text("""
            SELECT client_id,
                   client_secret,
                   redirect_uri,
                   user_id,
                   name,
                   oauth_client.desc,
                   website
              FROM oauth_client
             WHERE user_id = :user_id
        """), {
            "user_id": user_id
        })

        rows = result.fetchall()
    return [dict(row) for row in rows]


def tokens(user_id):
    """Get the oauth_tokens from a user_id.

    Args:
        user_id(uuid): ID of the user.

    Returns:
        List of dictionaries of client tokens of the user
        {
            "id": (int),
            "client_id": (str),
            "access_token": (str),
            "refresh_token": (str),
            "expires": (datetime),
            "scopes": (str)
            "client_name": (str),
            "client_website": (str),
        }
    """
    with db.engine.connect() as connection:
        result = connection.execute(sqlalchemy.text("""
            SELECT oauth_token.id,
                   oauth_token.client_id,
                   oauth_token.access_token,
                   oauth_token.refresh_token,
                   oauth_token.expires,
                   oauth_token.scopes,
                   oauth_client.name AS client_name,
                   oauth_client.website AS client_website
              FROM oauth_token
              JOIN oauth_client
                ON oauth_token.client_id = oauth_client.client_id
             WHERE oauth_token.user_id = :user_id
        """), {
            "user_id": user_id
        })

        rows = result.fetchall()
    return [dict(row) for row in rows]


def get_by_mb_row_id(musicbrainz_row_id, musicbrainz_id=None):
    """ Get user with specified MusicBrainz row ID.

    Note: this function optionally takes a MusicBrainz username to fall back on
    if no user with specified MusicBrainz row ID is found.

    Args:
        musicbrainz_row_id (int): the MusicBrainz row ID of the user
        musicbrainz_id (str): the MusicBrainz username of the user

    Returns:
        a dict representing the user if found, else None
    """
    filter_str = ""
    filter_data = {}
    if musicbrainz_id:
        filter_str = "OR (LOWER(musicbrainz_id) = LOWER(:musicbrainz_id) AND musicbrainz_row_id IS NULL)"
        filter_data["musicbrainz_id"] = musicbrainz_id

    filter_data["musicbrainz_row_id"] = musicbrainz_row_id
    with db.engine.connect() as connection:
        result = connection.execute(sqlalchemy.text("""
            SELECT {columns}
              FROM "user"
             WHERE musicbrainz_row_id = :musicbrainz_row_id
             {optional_filter}
        """.format(columns=','.join(USER_GET_COLUMNS), optional_filter=filter_str)), filter_data)

        if result.rowcount:
            return dict(result.fetchone())
        return None
