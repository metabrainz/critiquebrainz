from datetime import datetime
import uuid
from hashlib import md5
from critiquebrainz import db
from critiquebrainz.db import revision as db_revision
import sqlalchemy


def gravatar_url(source, default="identicon", rating="pg"):
    """Generates Gravatar URL from a source ID.

    Source string is hashed using the MD5 algorithm and included into a
    resulting URL. User's privacy should be considered when using this. For
    example, if using an email address, make sure that user explicitly allowed
    that.

    See https://en.gravatar.com/site/implement/images/ for implementation
    details.

    Args:
        source (str): String to be hashed and used as an avatar ID with the
            Gravatar service. Can be email, MusicBrainz username, or any other
            unique identifier.
        default (str): Default image to use if image for specified source is
            not found. Can be one of defaults provided by Gravatar (referenced
            by a keyword) or a publicly available image (as a full URL).
        rating (string): One of predefined audience rating values. Current
            default is recommended.

    Returns:
        URL to the Gravatar image.
    """
    return "https://gravatar.com/avatar/{hash}?d={default}&r={rating}".format(
        hash=md5(source.encode('utf-8')).hexdigest(),
        default=default,
        rating=rating,
    )


def get_many_by_mb_username(usernames):
    """Get information about users.

    Args:
        usernames (list): A list of MusicBrainz usernames. This lookup is case-insensetive.

    Returns:
        All columns of 'user' table (list of dictionaries)
        and avatar_url (Gravatar url).
        If the 'usernames' variable is an empty list function returns it back.
    """
    if not usernames:
        return []

    with db.engine.connect() as connection:
        result = connection.execute(sqlalchemy.text("""
            SELECT id,
                   display_name,
                   email,
                   created,
                   musicbrainz_id,
                   show_gravatar
              FROM "user"
             WHERE musicbrainz_id ILIKE ANY(:musicbrainz_usernames)
        """), {
            'musicbrainz_usernames': usernames,
        })
        row = result.fetchall()
        users = [dict(r) for r in row]
        for user in users:
            default_gravatar_src = "%s@cb" % user["id"]
            user["musicbrainz_username"] = user.pop("musicbrainz_id")
            if user["show_gravatar"]:
                user["avatar_url"] = gravatar_url(user.get("email") or default_gravatar_src)
            else:
                user["avatar_url"] = gravatar_url(default_gravatar_src)
        return users


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
            "show_gravatar": (bool),
            "is_blocked": (bool)
        }
    """
    with db.engine.connect() as connection:
        result = connection.execute(sqlalchemy.text("""
            SELECT id,
                   display_name,
                   email,
                   created,
                   musicbrainz_id,
                   show_gravatar,
                   is_blocked
              FROM "user"
             WHERE id = :user_id
        """), {
            "user_id": user_id
        })
        row = result.fetchone()
        if not row:
            return None
        row = dict(row)
        row['musicbrainz_username'] = row.pop('musicbrainz_id')
    return row


def create(**user_data):
    """Create user using the given details.

    Args:
        display_name(str): display_name of the user.
        musicbrainz_username(str, optional): musicbrainz username of user.
        email(str, optional): email of the user.
        show_gravatar(bool, optional): whether to show gravatar(default: false).
        is_blocked(bool, optional): whether user is blocked(default: false).

    Returns:
        Dictionary with the following structure:
        {
            "id": (uuid),
            "display_name": (str),
            "email": (str),
            "created": (datetime),
            "musicbrainz_username": (str),
            "show_gravatar": (bool),
            "is_blocked": (bool)
        }
    """
    display_name = user_data.pop('display_name')
    musicbrainz_username = user_data.pop('musicbrainz_username', None)
    email = user_data.pop('email', None)
    show_gravatar = user_data.pop('show_gravatar', False)
    is_blocked = user_data.pop('is_blocked', False)
    if user_data:
        raise TypeError('Unexpected **user_data: %r' % user_data)

    with db.engine.connect() as connection:
        result = connection.execute(sqlalchemy.text("""
            INSERT INTO "user" (id, display_name, email, created, musicbrainz_id, show_gravatar, is_blocked)
                 VALUES (:id, :display_name, :email, :created, :musicbrainz_id, :show_gravatar, :is_blocked)
              RETURNING id
        """), {
            "id": str(uuid.uuid4()),
            "display_name": display_name,
            "email": email,
            "created": datetime.now(),
            "musicbrainz_id": musicbrainz_username,
            "show_gravatar": show_gravatar,
            "is_blocked": is_blocked,
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
            "show_gravatar": (bool),
            "is_blocked": (bool)
        }
    """
    with db.engine.connect() as connection:
        result = connection.execute(sqlalchemy.text("""
            SELECT id,
                   display_name,
                   email,
                   created,
                   musicbrainz_id,
                   show_gravatar,
                   is_blocked
            FROM "user"
            WHERE musicbrainz_id = :musicbrainz_username
        """), {
            "musicbrainz_username": musicbrainz_username
        })
        row = result.fetchone()
        if not row:
            return None
        row = dict(row)
        row['musicbrainz_username'] = row.pop('musicbrainz_id')
    return row


def get_or_create(musicbrainz_username, new_user_data):
    """Get user from display_name and musicbrainz_username.

    Args:
        musicbrainz_username(str): MusicBrainz username of the user.
        new_user_data(dict): Dictionary containing the user data which may
                             contain the following keys:
        {
            "display_name": Display name of the user.
            "email": email of the user(optional).
            "show_gravatar": whether to show gravatar(default: false, optional).
            "is_blocked": whether user is blocked(default: false, optional).
        }

    Returns:
        Dictionary with the following structure:
        {
            "id": (uuid),
            "display_name": (str),
            "email": (str),
            "created": (datetime),
            "musicbrainz_username": (str),
            "show_gravatar": (bool),
            "is_blocked": (bool)
        }
    """
    user = get_by_mbid(musicbrainz_username)
    if not user:
        display_name = new_user_data.pop("display_name")
        user = create(display_name=display_name, musicbrainz_username=musicbrainz_username, **new_user_data)
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
            "show_gravatar": (bool),
            "is_blocked": (bool)
        }
    """
    with db.engine.connect() as connection:
        result = connection.execute(sqlalchemy.text("""
            SELECT id,
                   display_name,
                   email,
                   created,
                   musicbrainz_id,
                   show_gravatar,
                   is_blocked
              FROM "user"
             LIMIT :limit
            OFFSET :offset
        """), {
            "limit": limit,
            "offset": offset
        })
        rows = result.fetchall()
        rows = [dict(row) for row in rows]
        for row in rows:
            row['musicbrainz_username'] = row.pop('musicbrainz_id')
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


def get_votes(user_id, from_date='1-1-1970'):
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


def get_reviews(user_id, from_date='1-1-1970'):
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


def update(user_id, user_new_info):
    """Update info of a user.

    Args:
        user_id: ID of user whose info is to be updated.
        user_new_info: Dictionary containing the new information for the user
        {
            "display_name": (str),
            "show_gravatar": (bool),
            "email": (str)
        }
    """
    updates = []
    if "display_name" in user_new_info:
        updates.append("display_name = :display_name")
    if "show_gravatar" in user_new_info:
        updates.append("show_gravatar = :show_gravatar")
    if "email" in user_new_info:
        updates.append("email = :email")

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
