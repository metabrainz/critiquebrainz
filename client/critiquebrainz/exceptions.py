class CritiqueBrainzError(Exception):
    """ Parent class for app exceptions. """
    pass

class APIError(CritiqueBrainzError):
    def __init__(self, code, desc='', status=400):
        self.code = code
        self.desc = desc
        self.status = status

class OAuthError(APIError):
    pass

