import sqlalchemy

from critiquebrainz import db
from critiquebrainz.db import exceptions as db_exceptions


def create(*, client_id, scopes, access_token, refresh_token, expires, user_id):
    """Add OAuth Token to database.

    Args:
        client_id (str): ID of the OAuth Client.
        scopes (str, optional): Space seperated set of scopes.
        access_token (str): Access Token that can be used to get data from API.
        refresh_token (str): Token that can be used to obtain new access token.
        expires (datetime): Time in which access token expires.
        user_id (uuid): ID of the user that manages the client.

    Returns:
        Dictionary with the following structure:
        {
            "id": (int),
            "client_id": (str),
            "access_token": (str),
            "refresh_token": (str),
            "expires": (datetime),
            "user_id": (uuid),
            "scopes": (str),
        }
    """
    token = {
        "client_id": client_id,
        "access_token": access_token,
        "refresh_token": refresh_token,
        "expires": expires,
        "user_id": user_id,
        "scopes": scopes,
    }
    with db.engine.begin() as connection:
        result = connection.execute(sqlalchemy.text("""
            INSERT INTO oauth_token(client_id, access_token, refresh_token, expires, scopes, user_id)
                 VALUES (:client_id, :access_token, :refresh_token, :expires, :scopes, :user_id)
              RETURNING id
        """), token)
        token["id"] = result.first().id
    return token


def list_tokens(*, client_id=None, refresh_token=None, access_token=None, limit=1, offset=None):
    """Returns the list of OAuth Tokens.

    Args:
        client_id (str, optional): ID of the OAuth Client.
        refresh_token (str, optional): Token that can be used to obtain new access token.
        access_token (str, optional): Access Token that can be used to get data from API.
        limit (int, optional): Max number of tokens to be returned by this method (default=1).
        offset (int): Offset that can be used in conjunction with the limit.

    Returns:
        List of dictionaries with the following structure:
        {
            "id": (int),
            "client_id": (str),
            "access_token": (str),
            "refresh_token": (str),
            "expires": (datetime),
            "user_id": (uuid),
            "scopes": (str),
            "client_name": (str),
            "client_website": (str),
        }
    """
    filters = []
    filter_data = {}

    if client_id is not None:
        filters.append("oauth_token.client_id = :client_id")
        filter_data["client_id"] = client_id
    if refresh_token is not None:
        filters.append("refresh_token = :refresh_token")
        filter_data["refresh_token"] = refresh_token
    if access_token is not None:
        filters.append("access_token = :access_token")
        filter_data["access_token"] = access_token
    filterstr = str()
    if filters:
        filterstr = " AND ".join(filters)
        filterstr = " WHERE " + filterstr

    filter_data["limit"] = limit
    filter_data["offset"] = offset

    with db.engine.connect() as connection:
        results = connection.execute(sqlalchemy.text("""
            SELECT oauth_token.id,
                   oauth_token.client_id,
                   oauth_token.access_token,
                   oauth_token.refresh_token,
                   oauth_token.expires,
                   oauth_token.user_id,
                   oauth_token.scopes,
                   oauth_client.name AS client_name,
                   oauth_client.website AS client_website
              FROM oauth_token
              JOIN oauth_client
                ON oauth_token.client_id = oauth_client.client_id
              {where_clause}
             LIMIT :limit
            OFFSET :offset
        """.format(where_clause=filterstr)), filter_data)
        rows = results.mappings()
        return [dict(row) for row in rows]


def delete(*, client_id=None, refresh_token=None, user_id=None):
    """Delete an OAuth Token.

    Args:
        client_id (str): ID of the OAuth Client.
        refresh_token (str): Token that can be used to obtain new access token.
        user_id (uuid): ID of the user managing the client.
    """
    filters = ["client_id = :client_id"]
    filter_data = dict(client_id=client_id)
    if refresh_token is not None:
        filters.append("refresh_token = :refresh_token")
        filter_data["refresh_token"] = refresh_token
    if user_id is not None:
        filters.append("user_id = :user_id")
        filter_data["user_id"] = user_id
    filterstr = " AND ".join(filters)
    with db.engine.begin() as connection:
        connection.execute(sqlalchemy.text("""
            DELETE
              FROM oauth_token
             WHERE {filterstr}
        """.format(filterstr=filterstr)), filter_data)


def get_scopes(token_id):
    """Returns the scopes of an application.

    Args:
        token_id (int): ID of the OAuth Token.
    Returns:
        scopes: (list).
    """
    with db.engine.connect() as connection:
        result = connection.execute(sqlalchemy.text("""
            SELECT scopes
              FROM oauth_token
             WHERE id = :token_id
        """), {
            "token_id": token_id,
        })
        scopes = result.fetchone()
    if not scopes:
        raise db_exceptions.NoDataFoundException("No token exists with ID: {}".format(token_id))
    if scopes[0] is None:
        return list()
    return scopes[0].split()
