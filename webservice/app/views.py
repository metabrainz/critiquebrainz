from flask import request, jsonify
from app.models import db, User, Publication, Rate
from app.utils import *
from app.exceptions import *
from app import app

# publications
@app.route('/publication/<uuid:publication_id>', methods=['GET'])            
def show_publication(publication_id, include=[]):
    """ Fetching a single publication entry """
    #TODO: If-Modified-Since support
    # fetching data
    try:
        include = fetch_from_url_include('include', _model=Publication)
    except MissingDataError:
        include = []
    
    publication = Publication.query.get_or_404(publication_id)
    response = jsonify(publication=publication.to_dict(include))
    return response
    
@app.route('/publication/<uuid:publication_id>', methods=['PUT'])
def update_publication(publication_id, user_id=None, text=None):
    """ Updating a publication """
    # fetching data
    user_id = fetch_from_json_uuid('user_id') # temporary
    text = fetch_from_json('text')
    
    publication = Publication.query.get_or_404(publication_id)
    
    # temporary BEGIN
    if publication.user_id != user_id:
        raise AbortError('No authorization', 403)
    # temporary END
    
    publication.text = text
    db.session.commit()
    response = jsonify(message='Request processed successfully',
                       id=publication.id)
    return response
    
@app.route('/publication/<uuid:publication_id>', methods=['DELETE'])
def delete_publication(publication_id):
    """ Delete a publication """
    # fetching data
    user_id = fetch_from_json_uuid('user_id') # temporary
    
    publication = Publication.query.get_or_404(publication_id)
    
    # temporary BEGIN
    if publication.user_id != user_id:
        raise AbortError('No authorization', 403)
    # temporary END
    
    db.session.delete(publication)
    db.session.commit()
    response = jsonify(message='Request processed successfully')
    return response
    
@app.route('/publication', methods=['GET'])
def list_publication():
    """ Fetching a list of publications """
    # fetch `user_id`
    try:
        user_id = fetch_from_url_uuid('user_id') # temporary
    except MissingDataError:
        user_id = None
        
    # fetch `release_group`
    try:
        release_group = fetch_from_url_uuid('release_group')
    except MissingDataError:
        release_group = None
    
    # assert at least one parameter
    if not user_id and not release_group:
        AbortError('Missing `user_id` and/or `release_group` arguments.')
        
    # fetch `limit`
    try:
        limit = fetch_from_url_int_range('limit', _min=1, _max=50)
    except MissingDataError:
        limit = 50
        
    # fetch `offset`
    try:
        offset = fetch_from_url_int('offset')
    except MissingDataError:
        offset = 0
        
    # fetch `rating`
    try:
        rating = fetch_from_url_int('rating')
    except MissingDataError:
        rating = 0
        
    # fetch `include`
    try:
        include = fetch_from_url_include('include', _model=Publication)
    except MissingDataError:
        include = []
    
    # subquery counting rates
    subquery = db.session.query(Rate.publication_id, db.func.count('*').\
               label('count')).group_by(Rate.publication_id).subquery()
               
    # query with outerjoined subquery
    query = db.session.query(Publication).\
            outerjoin((subquery, Publication.id == subquery.c.publication_id))

    if user_id: 
        query = query.filter(Publication.user_id==user_id)
    if release_group: 
        query = query.filter(Publication.release_group==release_group)
    
    query = query.filter(Publication.rating>=rating)
    count = query.count()
    query = query.order_by(Publication.rating.desc(), subquery.c.count.desc()).\
                  limit(limit).\
                  offset(offset)
    publications = query.all()
    response = jsonify(limit=limit, offset=offset, count=count,
                       publications=[r.to_dict(include) for r in publications])
    return response    

@app.route('/publication', methods=['POST'])
def post_publication():
    """ Posting a publication """
    # fetching data
    user_id = fetch_from_json_uuid('user_id') # temporary
    release_group = fetch_from_json_uuid('release_group')
    text = fetch_from_json('text')
    
    # temporary BEGIN
    user = User.query.get(user_id)
    if not user: raise AbortError('No such user')
    # temporary END
    
    publication = Publication(user, text, release_group)
    db.session.add(publication)
    db.session.commit()
    response = jsonify(message='Request processed successfully',
                       id=publication.id)
    return response
    
# exceptions and error handling
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
    
