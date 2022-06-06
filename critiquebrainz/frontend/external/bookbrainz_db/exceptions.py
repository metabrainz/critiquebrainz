class BBDatabaseException(Exception):
    """Base exception for all exceptions related to BookBrainz database"""
    pass


class InvalidTypeError(BBDatabaseException):
    """Exception related to wrong type in present functions"""
    pass


class InvalidIncludeError(BBDatabaseException):
    """Exception related to wrong includes in present functions"""
    pass


class NoDataFoundException(BBDatabaseException):
    """Exception to be raised when no data has been found"""
    pass

