class MBDatabaseException(Exception):
    """Base exception for all exceptions related to MusicBrainz database"""
    pass


class InvalidIncludeError(MBDatabaseException):
    """Exception related to wrong includes in present functions"""
    pass


class NoDataFoundException(MBDatabaseException):
    """Exception to be raised when no data has been found"""
    pass
