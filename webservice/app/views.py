from flask import request, abort, jsonify
from app import app, db
from utils.decorators import require_uuid 
from models import Review

@app.route('/review/<uuid:review_id>', methods=['GET'])
def show_review(review_id):
    review = Review.query.get_or_404(review_id)
    response = jsonify(review=review.to_dict())
    return response
    
@app.route('/review', methods=['GET'])
@require_uuid('release_group')
def list_review(release_group):
    reviews = Review.query.filter(Review.release_group == release_group).\
        order_by(Review.rating).all()
    response = jsonify(reviews=[r.to_dict() for r in reviews])
    return response
