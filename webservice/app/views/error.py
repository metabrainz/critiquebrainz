from flask import jsonify, redirect
from app.exceptions import *
from app import app

@app.errorhandler(AbortError)
def handle_abort_error(error):
    resp = jsonify(error.to_dict())
    resp.status_code = error.status_code
    return resp

@app.errorhandler(RequestBodyNotValidJSONError)
def handle_request_body_not_valid_json_error(error):
    resp = handle_abort_error(
        AbortError('Request body is not a valid JSON object.'))
    return resp
    
@app.errorhandler(MissingDataError)
def handle_missing_data_error(error):
    resp = handle_abort_error(
        AbortError('Request missing `%s` parameter.' % error.entity))
    return resp
    
@app.errorhandler(NotValidDataError)
def handle_not_valid_data_error(error):
    resp = handle_abort_error(
        AbortError('Parameter `%s` is invalid.' % error.entity))
    return resp
    
@app.errorhandler(RequestError)
def handle_request_error(error):
    resp = handle_abort_error(
        AbortError('Could not complete processing the request.'))
    return resp

@app.errorhandler(500)
def handle_error_500(error):
    resp = handle_abort_error(AbortError('Internal server error', 500))
    return resp
    
@app.errorhandler(400)
def handle_error_400(error):
    resp = handle_abort_error(AbortError('Bad request', 400))
    return resp
    
@app.errorhandler(404)
def handle_error_404(error):
    resp = handle_abort_error(AbortError('Not found', 404))
    return resp
