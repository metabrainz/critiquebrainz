from hashlib import md5
import sqlalchemy
from critiquebrainz import db


def _avatar(user):
    url = "https://gravatar.com/avatar/{0}{1}"
    if user['email'] and user['show_gravatar']:
        return url.format(md5(user['email'].encode('utf-8')).hexdigest(),
                          "?d=identicon&r=pg")
    else:
        return url.format(md5(str(user['id']).encode('utf-8')).hexdigest(),
                          "?d=identicon")


def get_many_by_mb_username(usernames):
    """Get information on users
    Args:
        usernames (list): MusicBrainz usernames.
    Returns:
        All columns of "user" table (list of dictionaries)
        and avatar_url (Gravatar url)

    Ignores missing users
    """
    with db.engine.connect() as connection:
        result = connection.execute(sqlalchemy.text("""
          SELECT id,
                  display_name,
                  email,
                  created,
                  musicbrainz_id,
                  show_gravatar
          FROM "user"
          WHERE display_name IN :users"""), {'users': tuple(usernames)})
        row = result.fetchall()
        users = [dict(r) for r in row]
        for user in users:
            user["avatar_url"] = _avatar(user)
        return users
