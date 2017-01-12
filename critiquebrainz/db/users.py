from hashlib import md5
import sqlalchemy
from critiquebrainz import db


def avatar(user):
    """Args:
        user: user object from db (dict) or username string
    Returns:
        URL to gravatar image
    """
    url = "https://gravatar.com/avatar/{0}{1}"
    if type(user) is dict:
        if user['email'] and user['show_gravatar']:
            return url.format(md5(user['email'].encode('utf-8')).hexdigest(),
                              "?d=identicon&r=pg")
        else:
            return url.format(md5(str(user['id']).encode('utf-8')).hexdigest(),
                              "?d=identicon")
    return url.format(md5(user.encode('utf-8')).hexdigest(), "?d=identicon")


def get_many_by_mb_username(usernames):
    """Get information on users
    Args:
        usernames: A list of MusicBrainz usernames.
    Returns:
        All columns of 'user' table (list of dictionaries)
        and avatar_url (Gravatar url).
        If the 'usernames' variable is an empty list function returns it back.
    """

    with db.engine.connect() as connection:
        if not usernames:
            return []
        result = connection.execute(sqlalchemy.text("""
            SELECT id,
                   display_name,
                   email,
                   created,
                   musicbrainz_id,
                   show_gravatar
              FROM "user"
             WHERE musicbrainz_id IN :musicbrainz_usernames
        """), {
            'musicbrainz_usernames': tuple(usernames),
        })
        row = result.fetchall()
        users = [dict(r) for r in row]
        for user in users:
            user["avatar_url"] = avatar(user)
        return users
