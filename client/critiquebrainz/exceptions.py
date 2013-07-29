class CritiqueBrainzError(Exception):
    """ Parent class for app exceptions. """
    pass

class OAuthError(CritiqueBrainzError):
    _description = {'server_error': 'The authorization server encountered an '\
                        'unexpected condition that prevented it from '\
                        'fulfilling the request.',
                    'unauthorized_client': 'The client is not authorized to '\
                        'request an authorization code using this method.',
                    'unsupported_response_type': 'The authorization server does'\
                        'not support obtaining an authorization code using '\
                        'this method.',
                    'unsupported_grant_type': 'The authorization grant type is'\
                        'not supported by the authorization server.',
                    'invalid_redirect_uri': 'Invalid redirect uri.',
                    'invalid_scope': 'The requested scope is invalid, unknown, '\
                        'or malformed.',
                    'access_denied': 'The resource owner or authorization '\
                        'server denied the request.',
                    'invalid_client': 'Client authentication failed',
                    'invalid_grant': 'The provided authorization grant or '\
                        'refresh token is invalid, expired, revoked, or was '\
                        'issued to another client.',
                    'missing_redirect_uri': 'Missing redirect uri.'
                    }
    def __init__(self, code, status=400):
        self.code = code
        self.status = status

    @property
    def description(self):
        return self._description.get(self.code)

class APIError(OAuthError):
    pass

class SessionError(CritiqueBrainzError):
    pass