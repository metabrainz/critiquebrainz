from flask import request, abort, jsonify
from models import db, User, Review
from utils.decorators import require_uuid 
import oauth.decorators as oauth 

def register_views(app):
    app.add_url_rule('/review/<uuid:review_id>', view_func=show_review,
            methods=['GET'])
    app.add_url_rule('/review/<uuid:review_id>', view_func=update_review,
            methods=['PUT'])
    app.add_url_rule('/review/<uuid:review_id>', view_func=delete_review,
            methods=['DELETE'])
    app.add_url_rule('/review', view_func=list_review, methods = ['GET'])
    app.add_url_rule('/review', view_func=post_review, methods = ['POST'])

def show_review(review_id):
    ''' Fetching a single review entry '''
    review = Review.query.get_or_404(review_id)
    response = jsonify(review=review.to_dict())
    return response

@oauth.require_user
def update_review(review_id, user_id):
    ''' Updating a review '''
    review = Review.query.get_or_404(review_id)
    if review.user_id != user_id:
        abort(403)
    text = request.json.get('text')
    if text:
        review.text = text
    db.session.commit()
    response = jsonify(review=review.to_dict())
    return response

@oauth.require_user
def delete_review(review_id, user_id):
    ''' Delete a review '''
    review = Review.query.get_or_404(review_id)
    if review.user_id != user_id:
        abort(403)
    db.session.delete(review)
    db.session.commit()
    response = jsonify(id=review_id)
    return response

@require_uuid(arg='release_group')
def list_review(release_group):
    ''' Fetching a list of reviews relevant to a specified release group '''
    reviews = db.session.query(Review).filter(Review.release_group == release_group).\
        order_by(Review.rating).all()
    response = jsonify(reviews=[r.to_dict() for r in reviews])
    return response

@oauth.require_user
@require_uuid(json='release_group')
def post_review(release_group, user_id):
    ''' Posting a review '''
    user = db.session.query(User).filter(User.id==user_id).first()
    text = request.json.get('text') 
    review = Review(user, text, release_group)
    db.session.add(review)
    db.session.commit()
    response = jsonify(review=review.to_dict())
    return response
