from flask import request, redirect, jsonify

class CritiqueBrainzError(Exception):
    """ Parent class for app exceptions. """
    pass

class AbortError(CritiqueBrainzError):
    """ Exception raised when app cannot complete the request. """
    def __init__(self, message, status_code=400):
        super(AbortError, self).__init__(self)
        self.message = message
        self.status_code = status_code
            
    def to_dict(self):
        resp = dict(message=self.message)
        return resp
        
class OAuthError(CritiqueBrainzError):
    def __init__(self, code, status=400):
        self.code = code
        self.status = status

class LoginError(CritiqueBrainzError):
    def __init__(self, code, redirect_uri=None):
        self.code = code
        self.redirect_uri = redirect_uri
