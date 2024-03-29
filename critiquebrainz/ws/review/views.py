import logging

from brainzutils import cache
from flask import Blueprint, jsonify
from critiquebrainz.frontend.external import mbstore
from critiquebrainz.frontend.views import get_avg_rating
import critiquebrainz.db.review as db_review
from critiquebrainz.db import (
    vote as db_vote,
    exceptions as db_exceptions,
    spam_report as db_spam_report,
    revision as db_revision,
    users as db_users,
    REVIEW_RATING_MIN,
    REVIEW_RATING_MAX,
    REVIEW_TEXT_MIN_LENGTH,
    REVIEW_TEXT_MAX_LENGTH
)
from critiquebrainz.db.review import supported_languages, ENTITY_TYPES
from critiquebrainz.decorators import crossdomain
from critiquebrainz.ws.exceptions import NotFound, AccessDenied, InvalidRequest, LimitExceeded, MissingDataError, ParserError
from critiquebrainz.ws.oauth import oauth
from critiquebrainz.ws.parser import Parser
from critiquebrainz.utils import validate_uuid

review_bp = Blueprint('ws_review', __name__)

REVIEW_CACHE_NAMESPACE = "Review"
REVIEW_CACHE_TIMEOUT = 30 * 60  # 30 minutes


def get_review_or_404(review_id):
    """Get a review using review ID or raise error 404"""
    try:
        review = db_review.get_by_id(review_id)
    except db_exceptions.NoDataFoundException:
        raise NotFound(f"Can't find a review with ID: {review_id}")
    return review


@review_bp.route('/<uuid:review_id>', methods=['GET', 'OPTIONS'])
@crossdomain(headers="Authorization, Content-Type")
def review_entity_handler(review_id):
    """Get review with a specified UUID.

    **Request Example:**

    .. code-block:: bash

       $ curl https://critiquebrainz.org/ws/1/review/b7575c23-13d5-4adc-ac09-2f55a647d3de \\
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
              "info_url": "https://creativecommons.org/licenses/by-nc-sa/3.0/"
            },
            "popularity": 0,
            "source": "BBC",
            "source_url": "http://www.bbc.co.uk/music/reviews/3vfd",
            "text": "TEXT CONTENT OF REVIEW",
            "rating": 5,
            "user": {
              "created": "Wed, 07 May 2014 14:55:23 GMT",
              "display_name": "Paul Clarke",
              "id": "f5857a65-1eb1-4574-8843-ae6195de16fa",
              "karma": 0,
              "user_type": "Noob"
            },
            "votes": {
              "positive": 0,
              "negative": 0
            }
          }
        }

    :statuscode 200: no error
    :statuscode 404: review not found

    :resheader Content-Type: *application/json*
    """
    review = get_review_or_404(review_id)
    if review["is_hidden"]:
        raise NotFound("Review has been hidden.")
    return jsonify(review=db_review.to_dict(review))


@review_bp.route('/<uuid:review_id>/revisions', methods=['GET', 'OPTIONS'])
@crossdomain(headers="Authorization, Content-Type")
def review_revisions_handler(review_id):
    """Get revisions of review with a specified UUID.

    **Request Example:**

    .. code-block:: bash

        $ curl https://critiquebrainz.org/ws/1/review/b7575c23-13d5-4adc-ac09-2f55a647d3de/revisions \\
               -X GET

    **Response Example:**

    .. code-block:: json

        {
          "revisions": [
            {
              "id": 1,
              "review_id": "b7575c23-13d5-4adc-ac09-2f55a647d3de",
              "text": "TEXT CONTENT OF REVIEW",
              "rating": 5,
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
    review = get_review_or_404(review_id)
    if review["is_hidden"]:
        raise NotFound("Review has been hidden.")
    revisions = db_revision.get(review_id, limit=None)
    count = len(revisions)
    for i, r in enumerate(revisions):
        r.update(id=count - i)
    return jsonify(revisions=revisions)


@review_bp.route('/<uuid:review_id>/revisions/<int:rev>', methods=['GET', 'OPTIONS'])
@crossdomain(headers="Authorization, Content-Type")
def review_revision_entity_handler(review_id, rev):
    """Get a particular revisions of review with a specified UUID.

    **Request Example:**

    .. code-block:: bash

        $ curl https://critiquebrainz.org/ws/1/review/b7575c23-13d5-4adc-ac09-2f55a647d3de/revisions/1 \\
               -X GET

    **Response Example:**

    .. code-block:: json

        {
          "revision": {
            "id": 1,
            "review_id": "b7575c23-13d5-4adc-ac09-2f55a647d3de",
            "text": "TEXT CONTENT OF REVIEW",
            "rating": 5,
            "timestamp": "Tue, 10 Aug 2010 00:00:00 GMT",
            "votes_negative": 0,
            "votes_positive": 0
          }
        }

    :statuscode 200: no error
    :statuscode 404: review not found

    :resheader Content-Type: *application/json*
    """
    review = get_review_or_404(review_id)
    if review["is_hidden"]:
        raise NotFound("Review has been hidden.")

    count = db_revision.get_count(review["id"])
    if rev > count:
        raise NotFound("Can't find the revision you are looking for.")

    revision = db_revision.get(review_id, offset=count - rev)[0]
    revision.update(id=rev)
    return jsonify(revision=revision)


# don't need to add OPTIONS here because its already added
# for this endpoint in review_entity_handler
@review_bp.route('/<uuid:review_id>', methods=['DELETE'])
@oauth.require_auth('review')
@crossdomain(headers="Authorization, Content-Type")
def review_delete_handler(review_id, user):
    """Delete review with a specified UUID.

    **OAuth scope:** review

    **Request Example:**

    .. code-block:: bash

        $ curl "https://critiquebrainz.org/ws/1/review/9cb11424-d070-4ac1-8771-a8703ae5cccd" \\
               -X DELETE \\
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
    review = get_review_or_404(review_id)
    if review["is_hidden"]:
        raise NotFound("Review has been hidden.")
    if str(review["user_id"]) != user.id:
        raise AccessDenied
    db_review.delete(review_id)
    return jsonify(message='Request processed successfully')


# don't need to add OPTIONS here because its already added
# for this endpoint in review_entity_handler
@review_bp.route('/<uuid:review_id>', methods=['POST'])
@oauth.require_auth('review')
@crossdomain(headers="Authorization, Content-Type")
def review_modify_handler(review_id, user):
    """Update review with a specified UUID.

    **OAuth scope:** review

    :json string text: Text part of review, min length is 25, max is 5000 **(optional)**
    :json integer rating: Rating part of review, min is 1, max is 5 **(optional)**

    **NOTE:** Please provide only those parameters which need to be updated

    :statuscode 200: success
    :statuscode 400: invalid request
    :statuscode 403: access denied
    :statuscode 404: review not found

    :resheader Content-Type: *application/json*
    """

    def fetch_params(review):
        try:
            text = Parser.string('json', 'text', min=REVIEW_TEXT_MIN_LENGTH, max=REVIEW_TEXT_MAX_LENGTH)
        except MissingDataError:
            text = review['text']
        try:
            rating = Parser.int('json', 'rating', min=REVIEW_RATING_MIN, max=REVIEW_RATING_MAX)
        except MissingDataError:
            rating = review['rating']
        if text is None and rating is None:
            raise InvalidRequest(desc='Review must have either text or rating')
        return text, rating

    review = get_review_or_404(review_id)
    if review["is_hidden"]:
        raise NotFound("Review has been hidden.")
    if str(review["user_id"]) != user.id:
        raise AccessDenied
    text, rating = fetch_params(review)
    if (text == review['text']) and (rating == review['rating']):
        return jsonify(message='Request processed successfully', review=dict(id=review["id"]))

    db_review.update(
        review_id=review_id,
        drafted=review["is_draft"],
        text=text,
        rating=rating
    )
    return jsonify(message='Request processed successfully',
                   review=dict(id=review["id"]))


@review_bp.route('/', methods=['GET', 'OPTIONS'])
@crossdomain(headers="Authorization, Content-Type")
def review_list_handler():
    """Get list of reviews.

    **Request Example:**

    .. code-block:: bash

        $ curl "https://critiquebrainz.org/ws/1/review/?limit=1&offset=50" \\
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
                "info_url": "https://creativecommons.org/licenses/by-nc-sa/3.0/"
              },
              "popularity": 0,
              "source": "BBC",
              "source_url": "http://www.bbc.co.uk/music/reviews/vh54",
              "text": "TEXT CONTENT OF REVIEW",
              "rating": 5,
              "user": {
                "created": "Wed, 07 May 2014 16:20:47 GMT",
                "display_name": "Jenny Nelson",
                "id": "3bf3fe0c-6db2-4746-bcf1-f39912113852",
                "karma": 0,
                "user_type": "Noob"
              },
              "votes": {
                "positive": 0,
                "negative": 0
              }
            }
          ]
        }

    :query entity_id: UUID of an entity to retrieve reviews for **(optional)**
    :query entity_type: ``musicbrainz`` (for reviews about MusicBrainz entities) or ``bookbrainz`` (for reviews about bookbrainz entities) or one of the following entity types :data:`critiquebrainz.db.review.ENTITY_TYPES` **(optional)**
    :query user_id: user's UUID **(optional)**
    :query sort: ``popularity`` or ``published_on`` **(optional)**. Defaults to ``published_on``
    :query sort_order: ``asc`` or ``desc`` **(optional)**. Defaults to ``desc``
    :query limit: results limit, min is 0, max is 50, default is 50 **(optional)**
    :query offset: result offset, default is 0 **(optional)**
    :query language: language code (ISO 639-1) **(optional)**
    :query review_type: ``review`` or ``rating``. If set, only return reviews which have a text review, or a rating **(optional)**
    :query include_metadata: ``true`` or ``false``. Include metadata of the entity **(optional)**

    **NOTE:** If entity_id is provided, then additional top-level item "average_rating" which includes the average of all ratings for this entity and the total count of these ratings is also included.

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
    sort = Parser.string('uri', 'sort', valid_values=['popularity', 'published_on', 'rating', 'created'], optional=True)
    sort_order = Parser.string('uri', 'sort_order', valid_values=['asc', 'desc'], optional=True)
    review_type = Parser.string('uri', 'review_type', valid_values=['rating', 'review'], optional=True)
    include_metadata = Parser.string('uri', 'include_metadata', optional=True)

    # "rating" and "created" sort values are deprecated and but allowed here for backward compatibility
    if sort == 'created':
        sort = 'published_on'
    if sort == 'rating':
        sort = 'popularity'

    if not sort:
        sort = 'published_on'
    if not sort_order:
        sort_order = 'desc'

    # If an entity_id is given, then also include the average rating for the entity.
    if entity_id:
        include_avg_rating = True
    else:
        include_avg_rating = False

    limit = Parser.int('uri', 'limit', min=1, max=50, optional=True) or 50
    offset = Parser.int('uri', 'offset', optional=True) or 0
    language = Parser.string('uri', 'language', min=2, max=3, optional=True)
    if language and language not in supported_languages:
        raise InvalidRequest(desc='Unsupported language')

    # TODO(roman): Ideally caching logic should live inside the model. Otherwise it
    # becomes hard to track all this stuff.

    cache_key = cache.gen_key('list', f'entity_id={entity_id}', f'user_id={user_id}', f'sort={sort}',
                              f'sort_order={sort_order}', f'entity_type={entity_type}', f'limit={limit}',
                              f'offset={offset}', f'language={language}', f'review_type={review_type}', f'include_metadata={include_metadata}')
    cached_result = cache.get(cache_key, REVIEW_CACHE_NAMESPACE)

    if cached_result:
        reviews = cached_result['reviews']
        count = cached_result['count']
        avg_rating_data = cached_result['avg_rating_data']
    else:
        reviews, count = db_review.list_reviews(
            entity_id=entity_id,
            entity_type=entity_type,
            user_id=user_id,
            sort=sort,
            sort_order=sort_order,
            limit=limit,
            offset=offset,
            language=language,
            review_type=review_type
        )

        reviews = [db_review.to_dict(p) for p in reviews]

        if include_metadata == 'true':
            entities = [(str(review["entity_id"]), review["entity_type"]) for review in reviews]
            entities_info = mbstore.get_multiple_entities(entities)

            retrieved_entity_mbids = entities_info.keys()
            reviews = [review for review in reviews if str(review["entity_id"]) in retrieved_entity_mbids]
            for review in reviews:
                review[review['entity_type']] = entities_info[str(review["entity_id"])]

        if include_avg_rating:
            if reviews and not entity_type:
                entity_type = reviews[0]["entity_type"] if reviews else None

            if entity_type:
                avg_rating_data = get_avg_rating(entity_id, entity_type)
                if avg_rating_data:
                    avg_rating_data = {
                        "rating": avg_rating_data["rating"],
                        "count": avg_rating_data["count"]
                    }
                else:
                    avg_rating_data = {
                        "rating": None,
                        "count": 0
                    }
            else:
                avg_rating_data = None
                include_avg_rating = False

        else:
            avg_rating_data = None

        cache.set(cache_key, {
            'reviews': reviews,
            'count': count,
            'avg_rating_data': avg_rating_data
        }, expirein=REVIEW_CACHE_TIMEOUT, namespace=REVIEW_CACHE_NAMESPACE)

        # When we cache the results of a request, we include (entity_id, user_id, sort, limit, offset, language, review_type)
        # in the cache key. When entity_id is edited or deleted, we need to expire all cache items for this entity.
        # To do this, we track all of the cache keys for the entity in a separate cache item, ws_cache_{entity_id}.
        # These keys are retrieved and all keys are expired in invalidate_ws_entity_cache.
        # For keys without an entity_id, we add them to a separate cache item ws_cache_entity_id_absent. The keys in
        # this set invalidated when any review is modified or updated.
        cache_keys_for_entity_id_key = cache.gen_key('ws_cache', entity_id if entity_id else 'entity_id_absent')
        cache.sadd(cache_keys_for_entity_id_key, cache_key,
                   expirein=REVIEW_CACHE_TIMEOUT,
                   namespace=REVIEW_CACHE_NAMESPACE)

    result = {"limit": limit, "offset": offset, "count": count, "reviews": reviews}
    if include_avg_rating:
        result["average_rating"] = avg_rating_data
    return jsonify(**result)


# don't need to add OPTIONS here because its already added
# for this endpoint in review_list_handler
@review_bp.route('/', methods=['POST'])
@oauth.require_auth('review')
@crossdomain(headers="Authorization, Content-Type")
def review_post_handler(user):
    """Publish a review.

    **OAuth scope:** review

    :reqheader Content-Type: *application/json*

    :json uuid entity_id: UUID of the entity that is being reviewed
    :json string entity_type: One of the supported reviewable entities. 'release_group' or 'event' etc.
    :json string text: Text part of review, min length is 25, max is 5000 **(optional)**
    :json integer rating: Rating part of review, min is 1, max is 5 **(optional)**
    :json string license_choice: license ID
    :json string language: language code (ISO 639-1), default is ``en`` **(optional)**
    :json boolean is_draft: whether the review should be saved as a draft or not, default is ``False`` **(optional)**

    **NOTE:** You must provide some text or rating for the review.

    :resheader Content-Type: *application/json*
    """

    def fetch_params():
        is_draft = Parser.bool('json', 'is_draft', optional=True) or False
        min_review_length = None if is_draft else REVIEW_TEXT_MIN_LENGTH
        entity_id = Parser.uuid('json', 'entity_id')
        entity_type = Parser.string('json', 'entity_type', valid_values=ENTITY_TYPES)
        text = Parser.string('json', 'text', min=min_review_length, max=REVIEW_TEXT_MAX_LENGTH, optional=True)
        rating = Parser.int('json', 'rating', min=REVIEW_RATING_MIN, max=REVIEW_RATING_MAX, optional=True)
        license_choice = Parser.string('json', 'license_choice')
        language = Parser.string('json', 'language', min=2, max=3, optional=True) or 'en'
        if text is None and rating is None:
            raise InvalidRequest(desc='Review must have either text or rating')
        if language and language not in supported_languages:
            raise InvalidRequest(desc='Unsupported language')
        if db_review.list_reviews(inc_drafts=True, inc_hidden=True, entity_id=entity_id, user_id=user.id)[1]:
            raise InvalidRequest(desc='You have already published a review for this {entity_name}'.format(
                entity_name=db_review.ENTITY_TYPES_MAPPING[entity_type]))
        return entity_id, entity_type, text, rating, license_choice, language, is_draft

    if user.is_review_limit_exceeded:
        raise LimitExceeded('You have exceeded your limit of reviews per day.')
    entity_id, entity_type, text, rating, license_choice, language, is_draft = fetch_params()
    review = db_review.create(
        user_id=user.id,
        entity_id=entity_id,
        entity_type=entity_type,
        text=text,
        rating=rating,
        license_id=license_choice,
        language=language,
        is_draft=is_draft,
    )
    return jsonify(message='Request processed successfully', id=review["id"])


@review_bp.route('/languages', methods=['GET', 'OPTIONS'])
@crossdomain(headers="Authorization, Content-Type")
def languages_list_handler():
    """Get list of supported review languages (language codes from ISO 639-1).

    **Example Request:**

    .. code-block:: bash

        $ curl https://critiquebrainz.org/ws/1/review/languages \\
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


@review_bp.route('/<uuid:review_id>/vote', methods=['GET', 'OPTIONS'])
@oauth.require_auth('vote')
@crossdomain(headers="Authorization, Content-Type")
def review_vote_entity_handler(review_id, user):
    """Get your vote for a specified review.

    **Request Example:**

    .. code-block:: bash

        $ curl "https://critiquebrainz.org/ws/1/review/9cb11424-d070-4ac1-8771-a8703ae5cccd/vote" \\
               -X GET \\
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
    review = get_review_or_404(review_id)
    if review["is_hidden"]:
        raise NotFound("Review has been hidden.")
    try:
        vote = db_vote.get(user_id=user.id, revision_id=review["last_revision"]["id"])
    except db_exceptions.NoDataFoundException:
        raise NotFound("Can't find your vote for this review.")
    return jsonify(vote)


@review_bp.route('/<uuid:review_id>/vote', methods=['PUT', 'OPTIONS'])
@oauth.require_auth('vote')
@crossdomain(headers="Authorization, Content-Type")
def review_vote_put_handler(review_id, user):
    """Set your vote for a specified review.

    **OAuth scope:** vote

    **Request Example:**

    .. code-block:: bash

        $ curl "https://critiquebrainz.org/ws/1/review/9cb11424-d070-4ac1-8771-a8703ae5cccd/vote" \\
               -X PUT \\
               -H "Content-type: application/json" \\
               -H "Authorization: Bearer <access token>" \\
               -d '{"vote":true}'

    **Response Example:**

    .. code-block:: json

        {
          "message": "Request processed successfully"
        }

    :json boolean vote: ``true`` if upvote, ``false`` if downvote

    **NOTE:** Voting on reviews without text is not allowed.

    :statuscode 200: success
    :statuscode 400: invalid request (see source)
    :statuscode 403: daily vote limit exceeded
    :statuscode 404: review not found

    :resheader Content-Type: *application/json*
    """

    def fetch_params():
        vote = Parser.bool('json', 'vote')
        return vote

    review = get_review_or_404(review_id)
    if review["is_hidden"]:
        raise NotFound("Review has been hidden.")
    vote = fetch_params()
    if str(review["user_id"]) == user.id:
        raise InvalidRequest(desc='You cannot rate your own review.')
    if review["text"] is None:
        raise InvalidRequest(desc='Voting on reviews without text is not allowed.')
    if user.is_vote_limit_exceeded and not db_users.has_voted(user.id, review_id):
        raise LimitExceeded('You have exceeded your limit of votes per day.')

    db_vote.submit(
        user_id=user.id,
        revision_id=review["last_revision"]["id"],
        vote=vote,  # overwrites an existing vote, if needed
    )

    return jsonify(message='Request processed successfully')


@review_bp.route('/<uuid:review_id>/vote', methods=['DELETE', 'OPTIONS'])
@oauth.require_auth('vote')
@crossdomain(headers="Authorization, Content-Type")
def review_vote_delete_handler(review_id, user):
    """Delete your vote for a specified review.

    **OAuth scope:** vote

    **Request Example:**

    .. code-block:: bash

        $ curl "https://critiquebrainz.org/ws/1/review/9cb11424-d070-4ac1-8771-a8703ae5cccd/vote" \\
               -X DELETE \\
               -H "Authorization: Bearer <access token>"

    **Response Example:**

    .. code-block:: json

        {
          "message": "Request processed successfully"
        }

    :resheader Content-Type: *application/json*
    """
    review = get_review_or_404(review_id)
    if review["is_hidden"]:
        raise NotFound("Review has been hidden.")
    try:
        vote = db_vote.get(user_id=user.id, revision_id=review["last_revision"]["id"])
    except db_exceptions.NoDataFoundException:
        raise InvalidRequest("Review is not rated yet.")
    db_vote.delete(user_id=vote["user_id"], revision_id=vote["revision_id"])
    return jsonify(message="Request processed successfully")


@review_bp.route('/<uuid:review_id>/report', methods=['POST', 'OPTIONS'])
@oauth.require_auth('vote')
@crossdomain(headers="Authorization, Content-Type")
def review_spam_report_handler(review_id, user):
    """Create spam report for a specified review.

    **OAuth scope:** vote

    :resheader Content-Type: *application/json*
    """
    review = get_review_or_404(review_id)
    if review["is_hidden"]:
        raise NotFound("Review has been hidden.")
    if review["user_id"] == user.id:
        raise InvalidRequest('own')
    db_spam_report.create(review["last_revision"]["id"], user.id, "Spam")
    return jsonify(message="Spam report created successfully")
