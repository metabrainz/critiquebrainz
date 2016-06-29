from flask import Blueprint, jsonify
from critiquebrainz.data.model.review import Review, supported_languages, ENTITY_TYPES
from critiquebrainz.data.model.vote import Vote
from critiquebrainz.data.model.spam_report import SpamReport
from critiquebrainz.ws.exceptions import NotFound, AccessDenied, InvalidRequest, LimitExceeded
from critiquebrainz.ws.oauth import oauth
from critiquebrainz.ws.parser import Parser
from critiquebrainz.decorators import crossdomain
from brainzutils import cache

review_bp = Blueprint('ws_review', __name__)

REVIEW_MAX_LENGTH = 100000
REVIEW_MIN_LENGTH = 25


@review_bp.route('/<uuid:review_id>', methods=['GET'])
@crossdomain()
def review_entity_handler(review_id):
    """Get review with a specified UUID.

    :statuscode 200: no error
    :statuscode 404: review not found

    :resheader Content-Type: *application/json*
    """
    review = Review.query.get_or_404(str(review_id))
    if review.is_hidden:
        raise NotFound("Review has been hidden.")
    return jsonify(review=review.to_dict())


@review_bp.route('/<uuid:review_id>/revisions', methods=['GET'])
@crossdomain()
def review_revisions_handler(review_id):
    """Get revisions of review with a specified UUID.

    :statuscode 200: no error
    :statuscode 404: review not found

    :resheader Content-Type: *application/json*
    """
    review = Review.query.get_or_404(str(review_id))
    if review.is_hidden:
        raise NotFound("Review has been hidden.")
    revisions = []
    for i, r in enumerate(review.revisions):
        revision = r.to_dict()
        revision.update(id=i+1)
        revisions.append(revision)
    return jsonify(revisions=revisions)


@review_bp.route('/<uuid:review_id>/revisions/<int:rev>', methods=['GET'])
@crossdomain()
def review_revision_entity_handler(review_id, rev):
    """Get a particular revisions of review with a specified UUID.

    :statuscode 200: no error
    :statuscode 404: review not found

    :resheader Content-Type: *application/json*
    """
    review = Review.query.get_or_404(str(review_id))
    if review.is_hidden:
        raise NotFound("Review has been hidden.")

    count = len(review.revisions)
    if rev > count:
        raise NotFound("Can't find the revision you are looking for.")

    revision = review.revisions[rev-1].to_dict()
    revision.update(id=rev)
    return jsonify(revision=revision)


@review_bp.route('/<uuid:review_id>', methods=['DELETE'])
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
    if review.is_hidden:
        raise NotFound("Review has been hidden.")
    if review.user_id != user.id:
        raise AccessDenied
    review.delete()
    return jsonify(message='Request processed successfully')


@review_bp.route('/<uuid:review_id>', methods=['POST'])
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
    if review.is_hidden:
        raise NotFound("Review has been hidden.")
    if review.user_id != user.id:
        raise AccessDenied
    text = fetch_params()
    review.update(text=text)
    return jsonify(message='Request processed successfully',
                   review=dict(id=review.id))


@review_bp.route('/', methods=['GET'])
@crossdomain()
def review_list_handler():
    """Get list of reviews.

    :json uuid entity_id: UUID of the release group that is being reviewed
    :json string entity_type: One of the supported reviewable entities. 'release_group' or 'event' etc. **(optional)**
    :query user_id: user's UUID **(optional)**
    :query sort: ``rating`` or ``created`` **(optional)**
    :query limit: results limit, min is 0, max is 50, default is 50 **(optional)**
    :query offset: result offset, default is 0 **(optional)**
    :query language: language code (ISO 639-1) **(optional)**

    :resheader Content-Type: *application/json*
    """
    # TODO: This checking is added to keep old clients working and needs to be removed.
    release_group = Parser.uuid('uri', 'release_group', optional=True)
    if release_group:
        entity_id = release_group
        entity_type = 'release_group'
    else:        
        entity_id = Parser.uuid('uri', 'entity_id', optional=True)
        entity_type = Parser.string('uri', 'entity_type', valid_values=ENTITY_TYPES, optional=True)

    user_id = Parser.uuid('uri', 'user_id', optional=True)
    sort = Parser.string('uri', 'sort', valid_values=['rating', 'created'], optional=True)
    limit = Parser.int('uri', 'limit', min=1, max=50, optional=True) or 50
    offset = Parser.int('uri', 'offset', optional=True) or 0
    language = Parser.string('uri', 'language', min=2, max=3, optional=True)
    if language and language not in supported_languages:
        raise InvalidRequest(desc='Unsupported language')

    # TODO(roman): Ideally caching logic should live inside the model. Otherwise it
    # becomes hard to track all this stuff.
    cache_key = cache.gen_key('list', entity_id, user_id, sort, limit, offset, language)
    cached_result = cache.get(cache_key, Review.CACHE_NAMESPACE)
    if cached_result:
        reviews = cached_result['reviews']
        count = cached_result['count']

    else:
        reviews, count = Review.list(
            entity_id=entity_id,
            entity_type=entity_type,
            user_id=user_id,
            sort=sort,
            limit=limit,
            offset=offset,
            language=language,
        )
        reviews = [p.to_dict() for p in reviews]
        cache.set(cache_key, {
            'reviews': reviews,
            'count': count,
        }, namespace=Review.CACHE_NAMESPACE)

    return jsonify(limit=limit, offset=offset, count=count, reviews=reviews)


@review_bp.route('/', methods=['POST'])
@oauth.require_auth('review')
@crossdomain()
def review_post_handler(user):
    """Publish a review.

    **OAuth scope:** review

    :reqheader Content-Type: *application/json*

    :json uuid entity_id: UUID of the release group that is being reviewed
    :json string entity_type: One of the supported reviewable entities. 'release_group' or 'event' etc.
    :json string text: review contents, min length is 25, max is 5000
    :json string license_choice: license ID
    :json string lang: language code (ISO 639-1), default is ``en`` **(optional)**
    :json boolean is_draft: whether the review should be saved as a draft or not, default is ``False`` **(optional)**

    :resheader Content-Type: *application/json*
    """

    def fetch_params():
        is_draft = Parser.bool('json', 'is_draft', optional=True) or False
        if is_draft:
            REVIEW_MIN_LENGTH = None
        entity_id = Parser.uuid('json', 'entity_id')
        entity_type = Parser.string('json', 'entity_type', valid_values=ENTITY_TYPES)
        text = Parser.string('json', 'text', min=REVIEW_MIN_LENGTH, max=REVIEW_MAX_LENGTH)
        license_choice = Parser.string('json', 'license_choice')
        language = Parser.string('json', 'language', min=2, max=3, optional=True) or 'en'
        if language and language not in supported_languages:
            raise InvalidRequest(desc='Unsupported language')
        if Review.query.filter_by(user=user, entity_id=entity_id).count():
            raise InvalidRequest(desc='You have already published a review for this album')
        return entity_id, entity_type, text, license_choice, language, is_draft

    if user.is_review_limit_exceeded:
        raise LimitExceeded('You have exceeded your limit of reviews per day.')
    entity_id, entity_type, text, license_choice, language, is_draft = fetch_params()
    review = Review.create(user=user, entity_id=entity_id, entity_type=entity_type, text=text,
                           license_id=license_choice, language=language, is_draft=is_draft)
    return jsonify(message='Request processed successfully', id=review.id)


@review_bp.route('/languages', methods=['GET'])
@crossdomain()
def languages_list_handler():
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
    if review.is_hidden:
        raise NotFound("Review has been hidden.")
    vote = Vote.query.filter_by(user=user, revision=review.last_revision).first()
    if not vote:
        raise NotFound("Can't find your vote for this review.")
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
    if review.is_hidden:
        raise NotFound("Review has been hidden.")
    vote = fetch_params()
    if review.user_id == user.id:
        raise InvalidRequest(desc='You cannot rate your own review.')
    if user.is_vote_limit_exceeded is True and user.has_voted(review) is False:
        raise LimitExceeded('You have exceeded your limit of votes per day.')
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
    if review.is_hidden:
        raise NotFound("Review has been hidden.")
    vote = Vote.query.filter_by(user=user, revision=review.last_revision).first()
    if not vote:
        raise InvalidRequest(desc='Review is not rated yet.')
    vote.delete()
    return jsonify(message='Request processed successfully')


@review_bp.route('/<uuid:review_id>/report', methods=['POST'])
@oauth.require_auth('vote')
@crossdomain()
def review_spam_report_handler(review_id, user):
    """Create spam report for a specified review.

    **OAuth scope:** vote

    :resheader Content-Type: *application/json*
    """
    review = Review.query.get_or_404(str(review_id))
    if review.is_hidden:
        raise NotFound("Review has been hidden.")
    if review.user_id == user.id:
        raise InvalidRequest('own')
    SpamReport.create(review, user)
    return jsonify(message="Spam report created successfully")
