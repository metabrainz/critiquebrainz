from critiquebrainz import db
from critiquebrainz.db import exceptions as db_exceptions
import sqlalchemy


def getusers_id(usernames):
    """Get MusicBrainz ids of users
    Args:
        usernames (list): MusicBrainz usernames.
    """
    with db.engine.connect() as connection:
        req = sqlalchemy.text("""SELECT * FROM "user" WHERE display_name IN :users""")
        result = connection.execute(req, users=tuple(usernames))
        if not result:
            return db_exceptions.NoDataFoundException("Can't find users")
        row = result.fetchall()
        return row
