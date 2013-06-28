from flask import request, abort, jsonify
from app import app, db
from app.utils.decorators import uuid_or_400
from models import Review

@app.route('/review/<uuid:review_id>', methods=['GET'])
def show_review(review_id):
    review = Review.query.get_or_404(review_id)
    response = jsonify(review.to_dict())
    return response
    
@app.route('/review', methods=['GET'])
@uuid_or_400('release_group_id')
def list_review(release_group_id):
    reviews = Review.query.filter(Review.release_group_id == release_group_id). \
        order_by(Review.rating).all()
    response = jsonify(reviews=[r.to_dict() for r in reviews])
    return response
