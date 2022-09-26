import sqlalchemy

from critiquebrainz import db


def create(*, id, full_name, info_url=None):
    """Create a new license.

    Args:
        id (str): ID of the license.
        full_name (str): Full name of the license.
        info_url (str): Info URL for the license.
    Returns:
        Dict containing the following attributes
        {
            "id": (str),
            "full_name": (str),
            "info_url": (str),
        }
    """
    license = {
        "id": id,
        "full_name": full_name,
        "info_url": info_url,
    }
    with db.engine.begin() as connection:
        connection.execute(sqlalchemy.text("""
            INSERT INTO license(id, full_name, info_url)
                 VALUES (:id, :full_name, :info_url)
        """), license)
    return license


def delete(*, id):
    """Delete a license.

    Args:
        id (str): ID of the license.
    """
    with db.engine.begin() as connection:
        connection.execute(sqlalchemy.text("""
            DELETE
              FROM license
             WHERE id = :id
        """), {
            "id": id,
        })


def get_licenses_list(connection):
    """
        helper function for list_licenses() that extends support for execution within a transaction by directly receiving the
        connection object
    """
    query = sqlalchemy.text("""
        SELECT id,
               info_url,
               full_name
          FROM license
    """)
    results = connection.execute(query)
    return [dict(row) for row in results.mappings()]


def list_licenses():
    """Get a list of licenses.

    Returns:
        List of dictionaries with the following structure
        {
            "id": (str),
            "info_url": (str),
            "full_name": (str),
        }
    """
    with db.engine.connect() as connection:
        return get_licenses_list(connection)
