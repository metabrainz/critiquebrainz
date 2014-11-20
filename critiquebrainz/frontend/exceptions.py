from flask_babel import gettext


class FrontendError(Exception):
    """Base class for app exceptions."""
    pass


class InvalidRequest(FrontendError):
    def __init__(self, desc=None):
        self.status = 400
        self.desc = desc


class AccessDenied(FrontendError):
    def __init__(self, desc=gettext('Access to the requested resource has been denied')):
        self.status = 403
        self.desc = desc


class NotFound(FrontendError):
    def __init__(self, desc=None):
        self.status = 404
        self.desc = desc
