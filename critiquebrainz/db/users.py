from hashlib import md5
import sqlalchemy
from critiquebrainz import db


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
