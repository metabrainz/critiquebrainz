from flask import request, jsonify
from app.models import db, User, Publication, Rate
from app.utils import *
from app.exceptions import *
from app import app, oauth

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
@oauth.require_oauth('publication')
def update_publication(publication_id, data):
    """ Updating a publication """
    text = fetch_from_json('text')
    user = data.user
    publication = Publication.query.get_or_404(publication_id)
    
    if publication.user_id != user.id:
        raise AbortError('No authorization', 403)
    
    publication.text = text
    db.session.commit()
    response = jsonify(message='Request processed successfully',
                       id=publication.id)
    return response
    
@app.route('/publication/<uuid:publication_id>', methods=['DELETE'])
@oauth.require_oauth('publication')
def delete_publication(publication_id, data):
    """ Delete a publication """
    user = data.user    
    publication = Publication.query.get_or_404(publication_id)
    
    if publication.user_id != user.id:
        raise AbortError('No authorization', 403)
    
    db.session.delete(publication)
    db.session.commit()
    response = jsonify(message='Request processed successfully')
    return response
    
@app.route('/publication', methods=['GET'])
def list_publication():
    """ Fetching a list of publications """
    # fetch `user_id`
    try:
        user_id = fetch_from_url_uuid('user_id')
    except MissingDataError:
        user_id = None
        
    # fetch `release_group`
    try:
        release_group = fetch_from_url_uuid('release_group')
    except MissingDataError:
        release_group = None

    # assert at least one parameter
    if user_id is None and release_group is None:
        raise AbortError('Missing `user_id` and/or `release_group` arguments.')
        
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
@oauth.require_oauth('publication')
def post_publication(data):
    """ Posting a publication """
    release_group = fetch_from_json_uuid('release_group')
    text = fetch_from_json('text')
    user = data.user
    
    publication = Publication(user=user, text=text, release_group=release_group)
    db.session.add(publication)
    db.session.commit()
    response = jsonify(message='Request processed successfully',
                       id=publication.id)
    return response
    