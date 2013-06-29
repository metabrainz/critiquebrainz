from flask import request, abort, jsonify
from models import Review
from utils.decorators import require_uuid 

def register_views(app):
    app.add_url_rule('/review/<uuid:review_id>', view_func=show_review,
            methods=['GET',])
    app.add_url_rule('/review', view_func=list_review, methods = ['GET',])

def show_review(review_id):
    review = Review.query.get_or_404(review_id)
    response = jsonify(review=review.to_dict())
    return response
    
@require_uuid('release_group')
def list_review(release_group):
    reviews = Review.query.filter(Review.release_group == release_group).\
        order_by(Review.rating).all()
    response = jsonify(reviews=[r.to_dict() for r in reviews])
    return response
