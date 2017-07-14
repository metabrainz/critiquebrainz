class WebServiceError(Exception):
    def __init__(self, code='', desc=None, status=400, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.code = code
        self.desc = desc
        self.status = status


class LoginError(WebServiceError):
    def __init__(self, code, redirect_uri=None, *args, **kwargs):
        super().__init__(code=code, *args, **kwargs)
        self.redirect_uri = redirect_uri


class NotFound(WebServiceError):
    def __init__(self, desc=None, *args, **kwargs):
        super().__init__(code='not_found', desc=desc, status=404, *args, **kwargs)


class AccessDenied(WebServiceError):
    def __init__(self):
        super(AccessDenied, self).__init__(
            code='access_denied',
            desc='Access to the requested resource has been denied',
            status=403)


class NotAuthorized(WebServiceError):
    def __init__(self):
        super(NotAuthorized, self).__init__(
            code='not_authorized',
            desc='You need to be authorized to access the requested resource',
            status=401)


class ServerError(WebServiceError):
    def __init__(self):
        super(ServerError, self).__init__(
            code='server_error',
            desc='The authorization server encountered an unexpected '
                 'condition that prevented it from fulfilling the request.',
            status=500)


class LimitExceeded(WebServiceError):
    def __init__(self, desc=''):
        super(LimitExceeded, self).__init__(
            code='limit_exceeded',
            desc=desc,
            status=403)


class InvalidRequest(WebServiceError):
    def __init__(self, desc=''):
        super(InvalidRequest, self).__init__(
            code='invalid_request',
            desc=desc,
            status=400)


class ParserError(WebServiceError):
    def __init__(self, key, desc, *args, **kwargs):
        super().__init__(desc=desc, *args, **kwargs)
        self.key = key


class MissingDataError(ParserError):
    def __init__(self, key):
        super(MissingDataError, self).__init__(
            key=key,
            desc='missing')
