from hashlib import md5
import sqlalchemy
from critiquebrainz import db


def avatar(item):
    url = "https://gravatar.com/avatar/{0}{1}"
    email = item['email']
    if email and item['show_gravatar']:
        return url.format(md5(email.encode('utf-8')).hexdigest(), "?")
    else:
        return url


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
          SELECT "id", "display_name", "email", "created",
                  "musicbrainz_id", "show_gravatar"
          FROM "user"
          WHERE display_name IN :users"""), users=tuple(usernames))
        row = result.fetchall()
        users = [dict(_) for _ in row]
        for item in users:
            item.update({'avatar_url': avatar(item)})
        return users
