class DatabaseException(Exception):
    """Base exception for this package."""


class NoDataFoundException(DatabaseException):
    """Should be used when no data has been found."""


class BadDataException(DatabaseException):
    """Should be used when incorrect data is being submitted."""
