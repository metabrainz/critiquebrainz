class DatabaseException(Exception):
    """Base exception for this package."""
    pass


class NoDataFoundException(DatabaseException):
    """Should be used when no data has been found."""
    pass


class BadDataException(DatabaseException):
    """Should be used when incorrect data is being submitted."""
    pass

class IntegrityError(DatabaseException):
    """Should be used when any database constraint is violated"""
    pass
