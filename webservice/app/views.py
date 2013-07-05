from flask import request, abort, jsonify
from models import db, User, Publication, Rate
from utils.decorators import field 
from utils.uuid import validate

def register_views(app):
    app.add_url_rule('/publication/<uuid:publication_id>', 
            view_func=show_publication, methods=['GET'])
    app.add_url_rule('/publication/<uuid:publication_id>', 
            view_func=update_publication, methods=['PUT'])
    app.add_url_rule('/publication/<uuid:publication_id>', 
            view_func=delete_publication, methods=['DELETE'])
    app.add_url_rule('/publication', 
            view_func=list_publication, methods=['GET'])
    app.add_url_rule('/publication', 
            view_func=post_publication, methods=['POST'])
            
@field(arg='include', converter=(lambda x: x.split('+')), optional=True)
def show_publication(publication_id, include=[]):
    ''' Fetching a single publication entry '''
    #TODO: If-Modified-Since support
    for i in include:
        if i not in Publication.VALID_INCLUDES: abort(400)
    publication = Publication.query.get_or_404(publication_id)
    response = jsonify(publication=publication.to_dict(include))
    return response

@field(json='user_id')
@field(json='text')
def update_publication(publication_id, user_id=None, text=None):
    ''' Updating a publication '''
    publication = Publication.query.get_or_404(publication_id)
    if publication.user_id != user_id: abort(403)
    publication.text = text
    db.session.commit()
    response = jsonify(publication=publication.to_dict())
    return response

@field(json='user_id')
def delete_publication(publication_id, user_id=None):
    ''' Delete a publication '''
    if not validate(user_id): abort(400)
    publication = Publication.query.get_or_404(publication_id)
    if publication.user_id != user_id: abort(403)
    db.session.delete(publication)
    db.session.commit()
    response = jsonify(id=publication_id)
    return response

@field(arg='user_id', optional=True)
@field(arg='release_group', optional=True)
@field(arg='include', converter=(lambda x: x.split('+')), optional=True)
@field(arg='rating', converter=int, optional=True)
@field(arg='limit', converter=int, optional=True)
@field(arg='offset', converter=int, optional=True)
def list_publication(user_id=None, release_group=None, include=[], 
                     rating=0, limit=50, offset=0):
    ''' Fetching a list of publications relevant '''
    if not user_id and not release_group: abort(400)
    if limit not in range(1,51): abort(400)
    if rating not in range(-1,3): abort(400)
    for i in include:
        if i not in Publication.VALID_INCLUDES: abort(400)
    
    # subquery counting rates
    subquery = db.session.query(Rate.publication_id, db.func.count('*').\
               label('count')).group_by(Rate.publication_id).subquery()
               
    # query with outerjoin subquery to sort publications by rate count
    query = db.session.query(Publication).\
            outerjoin((subquery, Publication.id == subquery.c.publication_id))

    if user_id: 
        query = query.filter(Publication.user_id==user_id)
    if release_group: 
        query = query.filter(Publication.release_group==release_group)
    if rating:
        query = query.filter(Publication.rating>=rating)
    count = query.count()
    query = query.order_by(Publication.rating.desc(), subquery.c.count.desc()).\
                  limit(limit).\
                  offset(offset)
    publications = query.all()
    response = jsonify(limit=limit, offset=offset, count=count,
                       publications=[r.to_dict(include) for r in publications])
    return response    

@field(json='user_id')
@field(json='release_group')
@field(json='text')
def post_publication(user_id=None, release_group=None, text=None):
    ''' Posting a publication '''
    if not validate(user_id): abort(400)
    if not validate(release_group): abort(400)
    if not text: abort(400)
    
    user = User.query.get(user_id) or abort(403)
    publication = Publication(user, text, release_group)
    db.session.add(publication)
    db.session.commit()
    response = jsonify(publication=publication.to_dict())
    return response
