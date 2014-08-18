from flask import Blueprint, jsonify
from critiquebrainz.data.model.review import Review, supported_languages
from critiquebrainz.data.model.vote import Vote
from critiquebrainz.data.model.spam_report import SpamReport
from critiquebrainz.ws.exceptions import NotFound, AccessDenied, InvalidRequest, LimitExceeded
from critiquebrainz.ws.oauth import oauth
from critiquebrainz.ws.parser import Parser
from critiquebrainz.decorators import crossdomain

review_bp = Blueprint('ws_review', __name__)

REVIEW_MAX_LENGTH = 100000
REVIEW_MIN_LENGTH = 25


@review_bp.route('/<uuid:review_id>', endpoint='entity', methods=['GET'])
@crossdomain()
def review_entity_handler(review_id):
    """Get review with a specified UUID.

    :statuscode 200: no error
    :statuscode 404: review not found

    :resheader Content-Type: *application/json*
    """
    review = Review.query.get_or_404(str(review_id))
    if review.is_archived is True:
        raise NotFound
    return jsonify(review=review.to_dict())


@review_bp.route('/<uuid:review_id>', endpoint='delete', methods=['DELETE'])
@oauth.require_auth('review')
@crossdomain()
def review_delete_handler(review_id, user):
    """Delete review with a specified UUID.

    **OAuth scope:** review

    :statuscode 200: success
    :statuscode 403: access denied
    :statuscode 404: review not found

    :resheader Content-Type: *application/json*
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
@crossdomain()
def review_modify_handler(review_id, user):
    """Update review with a specified UUID.

    **OAuth scope:** review

    :statuscode 200: success
    :statuscode 403: access denied
    :statuscode 404: review not found

    :resheader Content-Type: *application/json*
    """

    def fetch_params():
        text = Parser.string('json', 'text', min=REVIEW_MIN_LENGTH, max=REVIEW_MAX_LENGTH)
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
@crossdomain()
def review_list_handler():
    """Get list of reviews.

    :query release_group: UUID of release group **(optional)**
    :query user_id: user's UUID **(optional)**
    :query sort: ``rating`` or ``created`` **(optional)**
    :query limit: results limit, min is 0, max is 50, default is 50 **(optional)**
    :query offset: result offset, default is 0 **(optional)**
    :query language: language code (ISO 639-1) **(optional)**

    :resheader Content-Type: *application/json*
    """

    def fetch_params():
        release_group = Parser.uuid('uri', 'release_group', optional=True)
        user_id = Parser.uuid('uri', 'user_id', optional=True)
        sort = Parser.string('uri', 'sort', valid_values=['rating', 'created'], optional=True) or 'rating'
        limit = Parser.int('uri', 'limit', min=1, max=50, optional=True) or 50
        offset = Parser.int('uri', 'offset', optional=True) or 0
        language = Parser.string('uri', 'language', min=2, max=3, optional=True)
        if language and language not in supported_languages:
            raise InvalidRequest(desc='Unsupported language')
        return release_group, user_id, sort, limit, offset, language

    release_group, user_id, sort, limit, offset, language = fetch_params()
    reviews, count = Review.list(release_group, user_id, sort, limit, offset, language)
    return jsonify(limit=limit, offset=offset, count=count,
                   reviews=[p.to_dict() for p in reviews])


@review_bp.route('/', endpoint='create', methods=['POST'])
@oauth.require_auth('review')
@crossdomain()
def review_post_handler(user):
    """Publish a review.

    **OAuth scope:** review

    :reqheader Content-Type: *application/json*

    :json uuid release_group: UUID of the release group that is being reviewed
    :json string text: review contents, min length is 25, max is 5000
    :json string license_choice: license ID
    :json string lang: language code (ISO 639-1), default is ``en`` **(optional)**

    :resheader Content-Type: *application/json*
    """

    def fetch_params():
        release_group = Parser.uuid('json', 'release_group')
        text = Parser.string('json', 'text', min=REVIEW_MIN_LENGTH, max=REVIEW_MAX_LENGTH)
        license_choice = Parser.string('json', 'license_choice')
        language = Parser.string('json', 'language', min=2, max=3, optional=True) or 'en'
        if language and language not in supported_languages:
            raise InvalidRequest(desc='Unsupported language')
        if Review.query.filter_by(user=user, release_group=release_group).count():
            raise InvalidRequest(desc='You have already published a review for this album')
        return release_group, text, license_choice, language

    if user.is_review_limit_exceeded:
        raise LimitExceeded('You have exceeded your limit of reviews per day.')
    release_group, text, license_choice, language = fetch_params()
    review = Review.create(user=user, release_group=release_group, text=text, license_id=license_choice,
                           language=language)
    return jsonify(message='Request processed successfully', id=review.id)


@review_bp.route('/languages', endpoint='languages', methods=['GET'])
@crossdomain()
def review_list_handler():
    """Get list of supported review languages (language codes from ISO 639-1).

    :resheader Content-Type: *application/json*
    """
    return jsonify(languages=supported_languages)


@review_bp.route('/<uuid:review_id>/vote', methods=['GET'])
@oauth.require_auth('vote')
@crossdomain()
def review_vote_entity_handler(review_id, user):
    """Get your vote for a specified review.

    **OAuth scope:** vote

    :resheader Content-Type: *application/json*
    """
    review = Review.query.get_or_404(str(review_id))
    vote = Vote.query.filter_by(user=user, review=review).first()
    if not vote:
        raise NotFound
    else:
        return jsonify(vote=vote.to_dict())


@review_bp.route('/<uuid:review_id>/vote', methods=['PUT'])
@oauth.require_auth('vote')
@crossdomain()
def review_vote_put_handler(review_id, user):
    """Set your vote for a specified review.

    **OAuth scope:** vote

    :json boolean vote: ``true`` if upvote, ``false`` if downvote

    :statuscode 200: success
    :statuscode 400: invalid request (see source)
    :statuscode 403: daily vote limit exceeded
    :statuscode 404: review not found

    :resheader Content-Type: *application/json*
    """

    def fetch_params():
        vote = Parser.bool('json', 'vote')
        return vote

    review = Review.query.get_or_404(str(review_id))
    if review.is_archived is True:
        raise NotFound
    vote = fetch_params()
    if review.user_id == user.id:
        raise InvalidRequest(desc='You cannot rate your own review.')
    if user.is_vote_limit_exceeded is True and user.has_voted(review) is False:
        raise LimitExceeded('You have exceeded your limit of votes per day.')
    if vote is True and user.user_type not in review.review_class.upvote:
        raise InvalidRequest(desc='You are not allowed to upvote this review.')
    if vote is False and user.user_type not in review.review_class.downvote:
        raise InvalidRequest(desc='You are not allowed to downvote this review.')
    Vote.create(user, review, vote)  # overwrites an existing vote, if needed
    return jsonify(message='Request processed successfully')


@review_bp.route('/<uuid:review_id>/vote', methods=['DELETE'])
@oauth.require_auth('vote')
@crossdomain()
def review_vote_delete_handler(review_id, user):
    """Delete your vote for a specified review.

    **OAuth scope:** vote

    :resheader Content-Type: *application/json*
    """
    review = Review.query.get_or_404(str(review_id))
    if review.is_archived is True:
        raise NotFound
    vote = Vote.query.filter_by(user=user, review=review).first()
    if not vote:
        raise InvalidRequest(desc='Review is not rated yet.')
    vote.delete()
    return jsonify(message='Request processed successfully')


@review_bp.route('/<uuid:review_id>/report', endpoint='report', methods=['POST'])
@oauth.require_auth('vote')
@crossdomain()
def review_spam_report_handler(review_id, user):
    """Create spam report for a specified review.

    **OAuth scope:** vote

    :resheader Content-Type: *application/json*
    """
    review = Review.query.get_or_404(str(review_id))
    if review.user_id == user.id:
        raise InvalidRequest('own')
    SpamReport.create(review, user)
    return jsonify(message="Spam report created successfully")
