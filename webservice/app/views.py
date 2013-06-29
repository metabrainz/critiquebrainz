from flask import request, abort, jsonify
from models import db, User, Review
from utils.decorators import require_uuid 

def register_views(app):
    app.add_url_rule('/review/<uuid:review_id>', view_func=show_review,
            methods=['GET'])
    app.add_url_rule('/review', view_func=list_review, methods = ['GET'])
    app.add_url_rule('/review', view_func=post_review, methods = ['POST'])

def show_review(review_id):
    ''' Fetching a single review entry '''
    review = Review.query.get_or_404(review_id)
    response = jsonify(review=review.to_dict())
    return response
    
@require_uuid('release_group')
def list_review(release_group):
    ''' Fetching a list of reviews relevant to a specified release group '''
    reviews = db.session.query(Review).filter(Review.release_group == release_group).\
        order_by(Review.rating).all()
    response = jsonify(reviews=[r.to_dict() for r in reviews])
    return response

@require_uuid('release_group')
@require_uuid('user_id') # used temporary for tests until oauth is done
def post_review(release_group, user_id):
    ''' Posting a review '''
    user = User.query.get(user_id)
    text = request.values.get('text') 
    review = Review(user, text, release_group)
    db.session.add(review)
    db.session.commit()
    response = jsonify(review=dict(id=review.id))
    return response
