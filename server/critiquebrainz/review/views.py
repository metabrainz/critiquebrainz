from flask import Blueprint, jsonify
from critiquebrainz.db import Review, Vote
from critiquebrainz.exceptions import *
from critiquebrainz.oauth import oauth
from critiquebrainz.parser import Parser

review_bp = Blueprint('review', __name__)

@review_bp.route('/<uuid:review_id>', endpoint='entity', methods=['GET'])
def review_entity_handler(review_id):
    """Get review with a specified UUID.

    :statuscode 200: no error
    :statuscode 404: review not found
    """
    review = Review.query.get_or_404(str(review_id))
    if review.is_archived is True:
        raise NotFound
    include = Parser.list('uri', 'inc', Review.allowed_includes, optional=True) or []
    return jsonify(review=review.to_dict(include))

@review_bp.route('/<uuid:review_id>', endpoint='delete', methods=['DELETE'])
@oauth.require_auth('review')
def review_delete_handler(review_id, user):
    """Delete review with a specified UUID.

    :statuscode 200: success
    :statuscode 403: access denied
    :statuscode 404: review not found
    """
    review = Review.query.get_or_404(str(review_id))
    if review.is_archived is True:
        raise NotFound
    if review.user_id != user.id:
        raise AccessDenied
    review.delete()
    return jsonify(message='Request processed successfully')

@review_bp.route('/<uuid:review_id>', endpoint='modify', methods=['POST'])
@oauth.require_auth('review')
def review_modify_handler(review_id, user):
    """Update review with a specified UUID.

    :statuscode 200: success
    :statuscode 403: access denied
    :statuscode 404: review not found
    """
    def fetch_params():
        text = Parser.string('json', 'text', min=25, max=2500)
        return text
    review = Review.query.get_or_404(str(review_id))
    if review.is_archived is True:
        raise NotFound
    if review.user_id != user.id:
        raise AccessDenied
    text = fetch_params()
    review.update(text=text)
    return jsonify(message='Request processed successfully',
                   review=dict(id=review.id))

@review_bp.route('/', endpoint='list', methods=['GET'])
def review_list_handler():
    """Get list of reviews.

    :query release_group: UUID of release group
    :query user_id: user's UUID
    :query sort: `rating` or `created`
    :query limit: results limit. min is 0, max is 50, default is 50
    :query offset: result offset. default is 0
    :query inc: includes
    """
    def fetch_params():
        release_group = Parser.uuid('uri', 'release_group', optional=True)
        user_id = Parser.uuid('uri', 'user_id', optional=True)
        sort = Parser.string('uri', 'sort', valid_values=['rating', 'created'], optional=True) or 'rating'
        limit = Parser.int('uri', 'limit', min=1, max=50, optional=True) or 50
        offset = Parser.int('uri', 'offset', optional=True) or 0
        include = Parser.list('uri', 'inc', Review.allowed_includes, optional=True) or []
        return release_group, user_id, sort, limit, offset, include
    release_group, user_id, sort, limit, offset, include = fetch_params()
    reviews, count = Review.list(release_group, user_id, sort, limit, offset)
    return jsonify(limit=limit, offset=offset, count=count,
                   reviews=[p.to_dict(include) for p in reviews])

@review_bp.route('/', endpoint='create', methods=['POST'])
@oauth.require_auth('review')
def review_post_handler(user):
    """Publish a review."""
    def fetch_params():
        release_group = Parser.uuid('json', 'release_group')
        text = Parser.string('json', 'text', min=25, max=2500)
        license_choice = Parser.string('json', 'license_choice')
        if Review.query.filter_by(user=user, release_group=release_group).count():
            raise InvalidRequest(desc='You have already published a review for this album')
        return release_group, text, license_choice
    if user.is_review_limit_exceeded:
        raise LimitExceeded('You have exceeded your limit of reviews per day.')
    release_group, text, license_choice = fetch_params()
    review = Review.create(user=user, release_group=release_group, text=text, license_id=license_choice)
    return jsonify(message='Request processed successfully',
                   id=review.id)

@review_bp.route('/<uuid:review_id>/vote', methods=['GET'])
@oauth.require_auth('vote')
def review_vote_entity_handler(review_id, user):
    """Get user's vote for a specified review."""
    review = Review.query.get_or_404(str(review_id))
    vote = Vote.query.filter_by(user=user, review=review).first()
    if not vote:
        raise NotFound
    else:
        return jsonify(vote=vote.to_dict())

@review_bp.route('/<uuid:review_id>/vote', methods=['PUT'])
@oauth.require_auth('vote')
def review_vote_put_handler(review_id, user):
    """Set user's vote for a specified review.

    :statuscode 200: success
    :statuscode 400: invalid request (see source)
    :statuscode 403: daily vote limit exceeded
    :statuscode 404: review not found
    """
    def fetch_params():
        placet = Parser.bool('json', 'placet')
        return placet
    review = Review.query.get_or_404(str(review_id))
    if review.is_archived is True:
        raise NotFound
    placet = fetch_params()
    if review.user_id == user.id:
        raise InvalidRequest(desc='You cannot rate your own review.')
    if user.is_vote_limit_exceeded is True and user.has_voted(review) is False:
        raise LimitExceeded('You have exceeded your limit of votes per day.')
    if placet is True and user.user_type not in review.review_class.upvote:
        raise InvalidRequest(desc='You are not allowed to upvote this review.')
    if placet is False and user.user_type not in review.review_class.downvote:
        raise InvalidRequest(desc='You are not allowed to downvote this review.')
    # overwrites an existing vote, if needed
    vote = Vote.create(user, review, placet)
    return jsonify(message='Request processed successfully')

@review_bp.route('/<uuid:review_id>/vote', methods=['DELETE'])
@oauth.require_auth('vote')
def review_vote_delete_handler(review_id, user):
    """Delete user's vote for a specified review."""
    review = Review.query.get_or_404(str(review_id))
    if review.is_archived is True:
        raise NotFound
    vote = Vote.query.filter_by(user=user, review=review).first()
    if not vote:
        raise InvalidRequest(desc='Review is not rated yet.')
    vote.delete()
    return jsonify(message='Request processed successfully')
