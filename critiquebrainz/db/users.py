from hashlib import md5
import critiquebrainz.db.revision as db_revision
import sqlalchemy
from critiquebrainz import db
from datetime import datetime
import uuid


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
            if user["show_gravatar"]:
                user["avatar_url"] = gravatar_url(user.get("email") or default_gravatar_src)
            else:
                user["avatar_url"] = gravatar_url(default_gravatar_src)
        return users


def get_by_id(user_id):
    """Get user from user_id

    Args:
        user_id(uuid): ID of the user

    Returns:
        Dictionary with the following structure:
        {
            "id": (uuid)
            "display_name": (str)
            "email": (str)
            "created": (datetime)
            "musicbrainz_id": (str)
            "show_gravatar": (bool)
            "is_blocked": (bool)
        }
    """
    with db.engine.connect() as connection:
        result = connection.execute(sqlalchemy.text("""
            SELECT id, display_name, email, created,
                   musicbrainz_id, show_gravatar, is_blocked
              FROM "user"
             WHERE id = :user_id
        """), {
            "user_id": user_id
        })
        row = result.fetchone()
    return dict(row) if row else None


def create(display_name, **kwargs):
    """Create user using the given details

    Args:
        display_name(str): display_name of the user,
        musicbrainz_id(str, optional): musicbrainz_id of user,
        email(str, optional): email of the user,
        show_gravatar(bool, optional): whether to show gravatar(default: false)
        is_blocked(bool, optional): whether user is blocked(default: false)

    Returns:
        Dictionary with the following structure:
        {
            "id": (uuid)
            "display_name": (str)
            "email": (str)
            "created": (datetime)
            "musicbrainz_id": (str)
            "show_gravatar": (bool)
            "is_blocked": (bool)
        }
    """
    id = str(uuid.uuid4())
    musicbrainz_id = kwargs.pop('musicbrainz_id', None)
    email = kwargs.pop('email', None)
    show_gravatar = kwargs.pop('show_gravatar', False)
    is_blocked = kwargs.pop('is_blocked', False)
    if(kwargs):
        raise TypeError('Unexpected **kwargs: %r' % kwargs)

    with db.engine.connect() as connection:
        result = connection.execute(sqlalchemy.text("""
            INSERT INTO "user"
                 VALUES (:id, :display_name, :email, :created, :musicbrainz_id, :show_gravatar, :is_blocked)
              RETURNING id
            """), {
                "id": id,
                "display_name": display_name,
                "email": email,
                "created": datetime.now(),
                "musicbrainz_id": musicbrainz_id,
                "show_gravatar": show_gravatar,
                "is_blocked": is_blocked
            })
        new_id = result.fetchone()[0]
        user = get_by_id(new_id)
    return user


def get_by_mbid(musicbrainz_id):
    """Get user by musicbrainz_id

    Args:
        musicbrainz_id(str): Musicbrainz ID of the User

    Returns:
        Dictionary with the following structure:
        {
            "id": (uuid)
            "display_name": (str)
            "email": (str)
            "created": (datetime)
            "musicbrainz_id": (str)
            "show_gravatar": (bool)
            "is_blocked": (bool)
        }
    """
    with db.engine.connect() as connection:
        result = connection.execute(sqlalchemy.text("""
            SELECT id, display_name, email, created,
                   musicbrainz_id, show_gravatar, is_blocked
            FROM "user"
            WHERE musicbrainz_id = :musicbrainz_id
        """), {
            "musicbrainz_id": musicbrainz_id
        })
        row = result.fetchone()
    return dict(row) if row else None


def get_or_create(display_name, musicbrainz_id, **kwargs):
    """Get user from display_name and musicbrainz_id

    Args:
        display_name(str): display_name of the user
        musicbrainz_id(str): Musicbrainz ID of the user
        email(str, optional): email of the user,
        show_gravatar(bool, optional): whether to show gravatar(default: false)
        is_blocked(bool, optional): whether user is blocked(default: false)

    Returns:
        Dictionary with the following structure:
        {
            "id": (uuid)
            "display_name": (str)
            "email": (str)
            "created": (datetime)
            "musicbrainz_id": (str)
            "show_gravatar": (bool)
            "is_blocked": (bool)
        }
    """
    user = get_by_mbid(musicbrainz_id)
    if not user:
        user = create(display_name, musicbrainz_id=musicbrainz_id, **kwargs)
    return user


def get_count():
    """Returns the total number of users

    Returns:
        count: (int)
    """
    with db.engine.connect() as connection:
        result = connection.execute(sqlalchemy.text("""
            SELECT count(*)
              FROM "user"
        """))
        count = result.fetchone()[0]
    return count


def list(limit=None, offset=0):
    """Returns the list of users of critiquebrainz

    Args:
        limit(int, optional): Number of users to be returned
        offset(int, optional): Number of initial users to skip

    Returns:
        List of dictionaries of users with the following structure:
        {
            "id": (uuid)
            "display_name": (str)
            "email": (str)
            "created": (datetime)
            "musicbrainz_id": (str)
            "show_gravatar": (bool)
            "is_blocked": (bool)
        }
    """
    with db.engine.connect() as connection:
        result = connection.execute(sqlalchemy.text("""
            SELECT id, display_name, email, created,
                   musicbrainz_id, show_gravatar, is_blocked
              FROM "user"
             LIMIT :limit
            OFFSET :offset
        """), {
            "limit": limit,
            "offset": offset
        })
        rows = result.fetchall()
        rows = [dict(row) for row in rows]
    return rows


def unblock(user_id):
    """Unblock user (admin only)

    Args:
        user_id(uuid): ID of user to be unblocked
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
    """Block user (admin only)

    Args:
        user_id(uuid): ID of user to be blocked
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
    """Check if a user has already voted a review

    Args:
        user_id(uuid): ID of the user
        review_id(uuid): ID of the review

    Returns:
        (bool): True if has voted else False
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
    """Get the karma of a user

    Args:
        user_id(uuid): ID of the user

    Returns:
        karma(int): the karma of the user
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
        _karma = 0
        for row in rows:
            if row.vote == True:
                _karma += 1
            else:
                _karma -= 1
    return _karma


def reviews(user_id):
    """Get list of reviews written by a user

    Args:
        user_id(uuid): ID of the user

    Returns:
        List of reviews written by the user with the structure:
        {
            "id": (uuid)
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
            SELECT id, entity_id, entity_type, user_id, edits,
                   is_draft, license_id, language, source, source_url
              FROM review
             WHERE user_id = :user_id
        """), {
            "user_id": user_id
        })

        rows = result.fetchall()
        rows = [dict(row) for row in rows]

    return rows


def get_votes(user_id, date='1-1-1970'):
    """Get votes by a user from a specified time

    Args:
        user_id(uuid): ID of the user
        date(datetime): Date from which votes submitted(default: UTC)

    Returns:
        List of votes submitted by the user from the time specified
        {
            "vote": (bool),
            "rated_at": (datetime)
        }
    """
    with db.engine.connect() as connection:
        result = connection.execute(sqlalchemy.text("""
            SELECT vote, rated_at
              FROM vote
             WHERE user_id = :user_id
               AND rated_at >= :date
        """), {
            "user_id": user_id,
            "date": date
        })

        rows = result.fetchall()
        rows = [dict(row) for row in rows]

    return rows


def get_reviews(user_id, date='1-1-1970'):
    """Get reviews by a user from a specified time

    Args:
        user_id(uuid): ID of the user,
        date(datetime): Date from which reviews submitted(default: UTC)

    Returns:
        List of reviews by the user from the time specified
        {
            "id": (uuid)
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
           SELECT *
           FROM review
      LEFT JOIN
        (SELECT review_id
              , min(timestamp)
             AS creation_time
           FROM revision
       GROUP BY review_id)
             AS review_create
             ON review.id = review_id
          WHERE user_id = :user_id
            AND creation_time > :date
        """), {
            "user_id": user_id,
            "date": date
        })

        rows = result.fetchall()
        rows = [dict(row) for row in rows]

    return rows


def update(user, display_name=None, email=None, show_gravatar=None):
    """Update info of a user

    Args:
        user: User object whose info is to be updated,
        display_name(str): Display name of user,
        email(str): Email of the user,
        show_gravatar(bool): whether to show gravatar
    """
    if display_name is None:
        display_name = user.display_name
    if show_gravatar is None:
        show_gravatar = user.show_gravatar
    if email is None:
        email = user.email

    with db.engine.connect() as connection:
        connection.execute(sqlalchemy.text("""
            UPDATE "user"
               SET display_name = :display_name,
                  show_gravatar = :show_gravatar,
                          email = :email
             WHERE id = :user_id
        """), {
            "user_id": user.id,
            "display_name": display_name,
            "show_gravatar": show_gravatar,
            "email": email
        })


def delete(user_id):
    """Delete a user
    Deletes user, votes, reviews, revisions and spam reports
    by it

    Args:
        user_id(uuid): ID of the user to be deleted
    """
    with db.engine.connect() as connection:
        connection.execute(sqlalchemy.text("""
            DELETE
              FROM "user"
             WHERE id = :user_id
        """), {
            "user_id": user_id
        })
        connection.execute(sqlalchemy.text("""
            DELETE
              FROM "vote"
             WHERE user_id = :user_id
        """), {
            "user_id": user_id
        })
        connection.execute(sqlalchemy.text("""
            DELETE
              FROM "spam_report"
             WHERE user_id = :user_id
        """), {
            "user_id": user_id
        })
    user_reviews = reviews(user_id)
    with db.engine.connect() as connection:
        for review in user_reviews:
            connection.execute(sqlalchemy.text("""
                DELETE
                  FROM review
                 WHERE id = :review_id
            """), {
                "review_id": review['id']
            })
            connection.execute(sqlalchemy.text("""
                DELETE
                  FROM revision
                 WHERE review_id = :review_id
            """), {
                "review_id": review['id']
            })


def clients(user_id):
    """Get list of oauth clients registered by user

    Args:
        user_id(uuid): ID of the user,

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
            SELECT client_id, client_secret, redirect_uri,
                   user_id, name, oauth_client.desc, website
              FROM oauth_client
             WHERE user_id = :user_id
        """), {
            "user_id": user_id
        })

        rows = result.fetchall()
        rows = [dict(row) for row in rows]
    return rows


def tokens(user_id):
    """Get the oauth_tokens from a user_id

    Args:
        user_id(uuid): ID of the user

    Returns:
        List of dictionaries of client tokens of the user
        {
            "id": (int),
            "client_id": (Unicode),
            "access_token": (Unicode),
            "refresh_token": (Unicode),
            "expires": (datetime),
            "scopes": (Unicode)
        }
    """
    with db.engine.connect() as connection:
        result = connection.execute(sqlalchemy.text("""
            SELECT id, client_id, access_token,
                   refresh_token, expires, scopes
              FROM oauth_token
             WHERE user_id = :user_id
        """), {
            "user_id": user_id
        })

        rows = result.fetchall()
        rows = [dict(row) for row in rows]
    return rows
