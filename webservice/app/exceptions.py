from flask import request, redirect, jsonify
from app import app

class CritiqueBrainzError(Exception):
    """ Parent class for app exceptions. """
    pass

class AbortError(CritiqueBrainzError):
    """ Exception raised when app cannot complete the request. """

    status_code = 400
    
    def __init__(self, message, status_code=None):
        super(AbortError, self).__init__(self)
        self.message = message
        if status_code is not None:
            self.status_code = status_code
            
    def to_dict(self):
        resp = dict(message=self.message)
        return resp
        
class RequestError(CritiqueBrainzError):
    """ Parent class for request-related exceptions. """
    pass
    
class RequestBodyNotValidJSONError(RequestError):
    """ Exception raised when request body is not a valid JSON object. """
    pass
        
class ParameterError(RequestError):
    """ Exception for errors related to request data. """
        
    def __init__(self, entity):
        super(ParameterError, self).__init__(self)
        self.entity = entity
        
class MissingDataError(ParameterError):
    """ Exception raised when request is missing required data. """
    pass
    
class NotValidDataError(ParameterError):
    """ Exception raised when request data is not valid. """
    pass

class AuthorizationError(CritiqueBrainzError):
    """ Excpetion raised when authorization process fails. """
    #TODO: implementation of this exception in OAuthlib class
    _description = {'invalid_request': 'The request is missing a required '\
                        'parameter, includes an invalid parameter value, '\
                        'includes a parameter more than once, or is otherwise '\
                        'malformed.',
                   'server_error': 'The authorization server encountered an '\
                        'unexpected condition that prevented it from '\
                        'fulfilling the request.',
                   'unsupported_response_type': 'Requested response type is '\
                        'unsupported.',
                   'unauthorized_client': 'Client is not authorized.',
                   'invalid_scope': 'The requested scope is invalid, unknown, '\
                        'or malformed.',
                   'access_denied': 'The resource owner or authorization '\
                        'server denied the request.'}

    def __init__(self, error):
        self.error = error

    @property
    def description(self):
        return self._description[self.error]

    def to_dict(self):
        resp = dict(error=self.error, 
                    error_description=self.description)
        return resp

class AuthenticationError(CritiqueBrainzError):
    """ Exception raised when authentication process fails. """