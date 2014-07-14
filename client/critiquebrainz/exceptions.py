class CritiqueBrainzError(Exception):
    """ Parent class for app exceptions. """
    pass


class NotFound(CritiqueBrainzError):
    def __init__(self, desc=None):
        super(NotFound, self).__init__()
        self.status = 404
        self.desc = desc


class APIError(CritiqueBrainzError):
    def __init__(self, status=500, desc=None, code=None):
        super(APIError, self).__init__()
        self.status = status
        if desc is not None:
            self.desc = desc
        if code is not None:
            self.code = code


class ServerError(APIError):
    def __init__(self, status=500, desc=None, code=None):
        super(ServerError, self).__init__(status, desc, code)


class OAuthError(APIError):
    pass
