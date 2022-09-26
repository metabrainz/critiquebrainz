import sqlalchemy

from critiquebrainz import db
from critiquebrainz.db import exceptions as db_exceptions


def create(*, client_id, scopes, code, expires, redirect_uri, user_id):
    """Add OAuth Grant to database.

    Args:
        client_id (str): ID of the OAuth Client.
        code (str): The authorization code returned from authorization request.
        expires (datetime): Time in which access token expires.
        redirect_uri (str): URL where response must be sent.
        scopes (str, optional): Space seperated set of scopes.
        user_id (uuid): ID of the user that manages the client.

    Returns:
        Dictionary with the following structure:
        {
            "id": (int),
            "client_id": (str),
            "code": (str),
            "expires": (datetime),
            "redirect_uri": (str),
            "user_id": (uuid),
            "scopes": (str),
        }
    """
    grant = {
        "client_id": client_id,
        "code": code,
        "expires": expires,
        "redirect_uri": redirect_uri,
        "user_id": user_id,
        "scopes": scopes,
    }
    with db.engine.begin() as connection:
        result = connection.execute(sqlalchemy.text("""
            INSERT INTO oauth_grant(client_id, code, expires, redirect_uri, scopes, user_id)
                 VALUES (:client_id, :code, :expires, :redirect_uri, :scopes, :user_id)
              RETURNING id
        """), grant)
        grant["id"] = result.fetchone()[0]
    return grant


def list_grants(*, client_id=None, code=None, limit=1, offset=None):
    """Returns the list of OAuth Grants.

    Args:
        client_id (str, optional): ID of the OAuth Client.
        code (str, optional): The authorization code returned from authorization request.
        limit (int, optional): Max number of grants to be returned by this method (default=1).
        offset (int): Offset that can be used in conjunction with the limit.

    Returns:
        List of dictionaries with the following structure:
        {
            "id": (int),
            "client_id": (str),
            "code": (str),
            "expires": (datetime),
            "redirect_uri": (str),
            "user_id": (uuid),
            "scopes": (str),
        }
    """
    filters = []
    filter_data = {}

    if client_id is not None:
        filters.append("client_id = :client_id")
        filter_data["client_id"] = client_id
    if code is not None:
        filters.append("code = :code")
        filter_data["code"] = code
    filterstr = str()
    if filters:
        filterstr = " AND ".join(filters)
        filterstr = " WHERE " + filterstr

    filter_data["limit"] = limit
    filter_data["offset"] = offset

    with db.engine.connect() as connection:
        results = connection.execute(sqlalchemy.text("""
            SELECT id,
                   client_id,
                   code,
                   expires,
                   user_id,
                   redirect_uri,
                   scopes
              FROM oauth_grant
              {where_clause}
             LIMIT :limit
            OFFSET :offset
        """.format(where_clause=filterstr)), filter_data)
        rows = results.fetchall()
    return [dict(row) for row in rows]


def delete(*, client_id, code):
    """Delete an OAuth Token.

    Args:
        client_id (str): ID of the OAuth Client.
        code (str): The authorization code returned from authorization request.
    """
    with db.engine.begin() as connection:
        connection.execute(sqlalchemy.text("""
            DELETE
              FROM oauth_grant
             WHERE client_id = :client_id
               AND code = :code
        """), {
            "client_id": client_id,
            "code": code,
        })


def get_scopes(grant_id):
    """Returns the scopes of an application.

    Args:
        grant_id (int): ID of the OAuth Grant.
    Returns:
        scopes: (list).
    """
    with db.engine.connect() as connection:
        result = connection.execute(sqlalchemy.text("""
            SELECT scopes
              FROM oauth_grant
             WHERE id = :grant_id
        """), {
            "grant_id": grant_id,
        })
        scopes = result.fetchone()
    if not scopes:
        raise db_exceptions.NoDataFoundException("No grant exists with ID: {grant_id}".format(grant_id=grant_id))
    if scopes[0] is None:
        return list()
    return scopes[0].split()
