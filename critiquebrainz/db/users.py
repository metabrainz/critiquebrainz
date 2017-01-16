from hashlib import md5
import sqlalchemy
from critiquebrainz import db


def avatar(user):
    """Args:
        user: user data (dict or str)
    Returns:
        URL to gravatar image
    """
    url = "https://gravatar.com/avatar/{0}{1}"
    link = (user, "?d=identicon")
    if type(user) is dict:
        if user['email'] and user['show_gravatar']:
            link = (user['email'], "?d=identicon&r=pg")
        else:
            link = (str(user['id']), "?d=identicon")
        return url.format(md5(link[0].encode('utf-8')).hexdigest(), link[1])
    return url.format(link[0], link[1])


def get_many_by_mb_username(usernames):
    """Get information on users
    Args:
        usernames: A list of MusicBrainz usernames.
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
             WHERE musicbrainz_id IN :musicbrainz_usernames
        """), {
            'musicbrainz_usernames': tuple(usernames),
        })
        row = result.fetchall()
        users = [dict(r) for r in row]
        for user in users:
            user["avatar_url"] = avatar(user)
        return users
