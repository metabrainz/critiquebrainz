from flask import request, abort, jsonify
from models import db, User, Publication
from utils.decorators import require_uuid 
import oauth.decorators as oauth 

def register_views(app):
    app.add_url_rule('/publication/<uuid:publication_id>', view_func=show_publication,
            methods=['GET'])
    app.add_url_rule('/publication/<uuid:publication_id>', view_func=update_publication,
            methods=['PUT'])
    app.add_url_rule('/publication/<uuid:publication_id>', view_func=delete_publication,
            methods=['DELETE'])
    app.add_url_rule('/publication', view_func=list_publication, methods = ['GET'])
    app.add_url_rule('/publication', view_func=post_publication, methods = ['POST'])

def show_publication(publication_id):
    ''' Fetching a single publication entry '''
    publication = Publication.query.get_or_404(publication_id)
    response = jsonify(publication=publication.to_dict())
    return response

@oauth.require_user
def update_publication(publication_id, user_id):
    ''' Updating a publication '''
    publication = Publication.query.get_or_404(publication_id)
    if publication.user_id != user_id:
        abort(403)
    text = request.json.get('text')
    if text:
        publication.text = text
    db.session.commit()
    response = jsonify(publication=publication.to_dict())
    return response

@oauth.require_user
def delete_publication(publication_id, user_id):
    ''' Delete a publication '''
    publication = publication.query.get_or_404(publication_id)
    if publication.user_id != user_id:
        abort(403)
    db.session.delete(publication)
    db.session.commit()
    response = jsonify(id=publication_id)
    return response

@require_uuid(arg='release_group')
def list_publication(release_group):
    ''' Fetching a list of publications relevant to a specified release group '''
    publications = db.session.query(Publication).filter(Publication.release_group == release_group).\
        order_by(Publication.rating).all()
    response = jsonify(publications=[r.to_dict() for r in publications])
    return response

@oauth.require_user
@require_uuid(json='release_group')
def post_publication(release_group, user_id):
    ''' Posting a publication '''
    user = db.session.query(User).filter(User.id==user_id).first()
    text = request.json.get('text') 
    publication = Publication(user, text, release_group)
    db.session.add(publication)
    db.session.commit()
    response = jsonify(publication=publication.to_dict())
    return response
