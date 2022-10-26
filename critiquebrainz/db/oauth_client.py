import sqlalchemy

from critiquebrainz import db
from critiquebrainz.db import exceptions as db_exceptions
from critiquebrainz.utils import generate_string

CLIENT_ID_LENGTH = 20
CLIENT_SECRET_LENGTH = 40


def create(*, user_id, name, desc, website, redirect_uri):
    """Creates new OAuth client and generates secret key for it.

    Args:
        user_id (uuid): ID of the user who manages the client.
        name (str): Name of the client.
        desc (str): Client description.
        website (str): Client web site.
        redirect_uri: URI where responses will be sent.
    Returns:
        Dictionary of the following structure
        {
            "client_id": str,
            "client_secret": str,
            "user_id": uuid,
            "name": str,
            "desc": desc,
            "website": website,
            "redirect_uri": redirect_uri,
        }
    """
    with db.engine.begin() as connection:
        row = connection.execute(sqlalchemy.text("""
            INSERT INTO oauth_client (client_id, client_secret, redirect_uri,
                        user_id, name, "desc", website)
                 VALUES (:client_id, :client_secret, :redirect_uri,
                        :user_id, :name, :desc, :website)
                  RETURNING client_id, client_secret, redirect_uri, user_id, name, "desc", website
        """), {
            "client_id": generate_string(CLIENT_ID_LENGTH),
            "client_secret": generate_string(CLIENT_SECRET_LENGTH),
            "redirect_uri": redirect_uri,
            "user_id": user_id,
            "name": name,
            "website": website,
            "desc": desc,
        })
        return dict(row.mappings().first())


def update(*, client_id, name=None, desc=None, website=None, redirect_uri=None):
    """Update information related to a OAuth client

    Args:
        client_id(str): Client ID.
        name(str, optional): Updated name of the client.
        desc(str, optional): Updated description of the client.
        website(str, optional): Client web site.
        redirect_uri(str, optional): URI where responses will be sent.
    """
    updates = []
    update_data = {}
    if name is not None:
        updates.append("name = :name")
        update_data["name"] = name
    if desc is not None:
        updates.append('"desc" = :desc')
        update_data["desc"] = desc
    if website is not None:
        updates.append("website = :website")
        update_data["website"] = website
    if redirect_uri is not None:
        updates.append("redirect_uri = :redirect_uri")
        update_data["redirect_uri"] = redirect_uri

    update_str = ", ".join(updates)
    update_data["client_id"] = client_id

    query = sqlalchemy.text("""
        UPDATE oauth_client
           SET {update_str}
         WHERE client_id = :client_id
    """.format(update_str=update_str))

    if update_str:
        with db.engine.begin() as connection:
            connection.execute(query, update_data)


def delete(client_id):
    """Delete OAuth client.

    Args:
        client_id(str): ID of the OAuth Client.
    """
    with db.engine.begin() as connection:
        connection.execute(sqlalchemy.text("""
            DELETE
              FROM oauth_client
             WHERE client_id = :client_id
        """), {
            "client_id": client_id,
        })


def get_client(client_id):
    """Get info about an OAuth Client.

    Args:
        client_id(str): ID of the client.
    Returns:
        Dict with the following structure:
        {
            "client_id": str,
            "client_secret": str,
            "redirect_uri": str,
            "user_id": uuid,
            "name": str,
            "desc": str,
            "website": str,
        }
    """
    with db.engine.connect() as connection:
        result = connection.execute(sqlalchemy.text("""
            SELECT client_id,
                   client_secret,
                   redirect_uri,
                   user_id,
                   name,
                   "desc",
                   website
              FROM oauth_client
             WHERE client_id = :client_id
        """), {
            "client_id": client_id,
        })
        row = result.mappings().first()
        if not row:
            raise db_exceptions.NoDataFoundException("Can't find OAuth client with ID: {id}".format(id=client_id))
        return dict(row)
