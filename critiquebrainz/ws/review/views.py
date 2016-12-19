from flask import Blueprint, jsonify
from critiquebrainz.data.model.review import Review, supported_languages, ENTITY_TYPES
from critiquebrainz.data.model.vote import Vote
from critiquebrainz.data.model.spam_report import SpamReport
from critiquebrainz.db import vote as db_vote, exceptions as db_exceptions
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

     **Request Example:**

    .. code-block:: bash

       $ curl https://critiquebrainz.org/ws/1/review/b7575c23-13d5-4adc-ac09-2f55a647d3de \
              -X GET

    **Response Example:**

    .. code-block:: json

        {
          "review": {
            "created": "Tue, 10 Aug 2010 00:00:00 GMT",
            "edits": 0,
            "entity_id": "03e0a99c-3530-4e64-8f50-6592325c2082",
            "entity_type": "release_group",
            "id": "b7575c23-13d5-4adc-ac09-2f55a647d3de",
            "language": "en",
            "last_updated": "Tue, 10 Aug 2010 00:00:00 GMT",
            "license": {
              "full_name": "Creative Commons Attribution-NonCommercial-ShareAlike 3.0 Unported",
              "id": "CC BY-NC-SA 3.0",
              "info_url": "https:\/\/creativecommons.org\/licenses\/by-nc-sa\/3.0\/"
            },
            "rating": 0,
            "source": "BBC",
            "source_url": "http:\/\/www.bbc.co.uk\/music\/reviews\/3vfd",
            "text": "REVIEW GOES HERE",
            "user": {
              "created": "Wed, 07 May 2014 14:55:23 GMT",
              "display_name": "Paul Clarke",
              "id": "f5857a65-1eb1-4574-8843-ae6195de16fa",
              "karma": 0,
              "user_type": "Noob"
            },
            "votes_negative": 0,
            "votes_positive": 0
          }
        }

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

    **Request Example:**

    .. code-block:: bash

        $ curl https://critiquebrainz.org/ws/1/review/b7575c23-13d5-4adc-ac09-2f55a647d3de/revisions \
               -X GET

    **Response Example:**

    .. code-block:: json

        {
          "revisions": [
            {
              "id": 1,
              "review_id": "b7575c23-13d5-4adc-ac09-2f55a647d3de",
              "text": "REVIEW TEXT GOES HERE",
              "timestamp": "Tue, 10 Aug 2010 00:00:00 GMT",
              "votes_negative": 0,
              "votes_positive": 0
            }
          ]
        }

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

    **Request Example:**

    .. code-block:: bash

        $ curl https://critiquebrainz.org/ws/1/review/b7575c23-13d5-4adc-ac09-2f55a647d3de/revisions/1 \
               -X GET

    **Response Example:**

    .. code-block:: json

        {
          "revision": {
            "id": 1,
            "review_id": "b7575c23-13d5-4adc-ac09-2f55a647d3de",
            "text": "REVIEW TEXT GOES HERE",
            "timestamp": "Tue, 10 Aug 2010 00:00:00 GMT",
            "votes_negative": 0,
            "votes_positive": 0
          }
        }

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

    **Request Example:**

    .. code-block:: bash

        $ curl "https://critiquebrainz.org/ws/1/review/9cb11424-d070-4ac1-8771-a8703ae5cccd" \
               -X DELETE \
               -H "Authorization: Bearer <access token>"

    **Response Example:**

    .. code-block:: json

        {
          "message": "Request processed successfully"
        }

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

    **Request Example:**

    .. code-block:: bash

        $ curl "https://critiquebrainz.org/ws/1/review/?limit=1&offset=50" \
                -X GET

    **Response Example:**

    .. code-block:: json

        {
          "count": 9197,
          "limit": 1,
          "offset": 50,
          "reviews": [
            {
              "created": "Fri, 16 May 2008 00:00:00 GMT",
              "edits": 0,
              "entity_id": "09259937-6477-3959-8b10-af1cbaea8e6e",
              "entity_type": "release_group",
              "id": "c807d0b4-0dd0-43fe-a7c4-d29bb61f389e",
              "language": "en",
              "last_updated": "Fri, 16 May 2008 00:00:00 GMT",
              "license": {
                "full_name": "Creative Commons Attribution-NonCommercial-ShareAlike 3.0 Unported",
                "id": "CC BY-NC-SA 3.0",
                "info_url": "https:\/\/creativecommons.org\/licenses\/by-nc-sa\/3.0\/"
              },
              "rating": 0,
              "source": "BBC",
              "source_url": "http:\/\/www.bbc.co.uk\/music\/reviews\/vh54",
              "text": "REVIEW TEXT GOES HERE",
              "user": {
                "created": "Wed, 07 May 2014 16:20:47 GMT",
                "display_name": "Jenny Nelson",
                "id": "3bf3fe0c-6db2-4746-bcf1-f39912113852",
                "karma": 0,
                "user_type": "Noob"
              },
              "votes_negative": 0,
              "votes_positive": 0
            }
          ]
        }

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

    :json uuid entity_id: UUID of the entity that is being reviewed
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

    **Example Request:**

    .. code-block:: bash

        $ curl https://critiquebrainz.org/ws/1/review/languages \
               -X GET

    **Example Response:**

    .. code-block:: json

        {
          "languages": [
            "aa",
            "ab",
            "af",
            "ak",
            "yo",
            "za",
            "zh",
            "zu"
          ]
        }

    :resheader Content-Type: *application/json*
    """
    return jsonify(languages=supported_languages)


@review_bp.route('/<uuid:review_id>/vote', methods=['GET'])
@oauth.require_auth('vote')
@crossdomain()
def review_vote_entity_handler(review_id, user):
    """Get your vote for a specified review.

    **Request Example:**

    .. code-block:: bash

        $ curl "https://critiquebrainz.org/ws/1/review/9cb11424-d070-4ac1-8771-a8703ae5cccd/vote" \
               -X GET \
               -H "Authorization: Bearer <access token>"

    **Response Example:**

    .. code-block:: json

            {
              "vote": {
                "vote": true,
                "voted_at": "Thu, 22 Dec 2016 11:49:56 GMT"
              }
            }

    **OAuth scope:** vote

    :resheader Content-Type: *application/json*
    """
    review = Review.query.get_or_404(str(review_id))
    if review.is_hidden:
        raise NotFound("Review has been hidden.")
    try:
        vote = db_vote.get(user_id=user.id, revision_id=review.last_revision.id)
    except db_exceptions.NoDataFoundException:
        raise NotFound("Can't find your vote for this review.")
    return jsonify(vote)


@review_bp.route('/<uuid:review_id>/vote', methods=['PUT'])
@oauth.require_auth('vote')
@crossdomain()
def review_vote_put_handler(review_id, user):
    """Set your vote for a specified review.

    **OAuth scope:** vote

    **Request Example:**

    .. code-block:: bash

        $ curl "https://critiquebrainz.org/ws/1/review/9cb11424-d070-4ac1-8771-a8703ae5cccd/vote" \
               -X PUT \
               -H "Content-type: application/json" \
               -H "Authorization: Bearer <access token>" \
               -d '{"vote":true}'

    **Response Example:**

    .. code-block:: json

        {
          "message": "Request processed successfully"
        }

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

    db_vote.submit(
        user_id=user.id,
        revision_id=review.last_revision.id,
        vote=vote,  # overwrites an existing vote, if needed
    )

    return jsonify(message='Request processed successfully')


@review_bp.route('/<uuid:review_id>/vote', methods=['DELETE'])
@oauth.require_auth('vote')
@crossdomain()
def review_vote_delete_handler(review_id, user):
    """Delete your vote for a specified review.

    **OAuth scope:** vote

    **Request Example:**

    .. code-block:: bash

        $ curl "https://critiquebrainz.org/ws/1/review/9cb11424-d070-4ac1-8771-a8703ae5cccd/vote" \
               -X DELETE \
               -H "Authorization: Bearer <access token>"

    **Response Example:**

    .. code-block:: json

        {
          "message": "Request processed successfully"
        }

    :resheader Content-Type: *application/json*
    """
    review = Review.query.get_or_404(str(review_id))
    if review.is_hidden:
        raise NotFound("Review has been hidden.")
    try:
        vote = db_vote.get(user_id=user.id, revision_id=review.last_revision.id)
    except db_exceptions.NoDataFoundException:
        raise InvalidRequest("Review is not rated yet.")
    db_vote.delete(user_id=vote["user_id"], revision_id=vote["revision_id"])
    return jsonify(message="Request processed successfully")


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
