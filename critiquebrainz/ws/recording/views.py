from flask import Blueprint, jsonify
import critiquebrainz.db.review as db_review
import critiquebrainz.db.rating_stats as db_rating_stats
from critiquebrainz.frontend.external.musicbrainz_db import recording as db_recording
from critiquebrainz.decorators import crossdomain
from critiquebrainz.ws.exceptions import NotFound
from critiquebrainz.ws.parser import Parser
from critiquebrainz.ws import REVIEWS_LIMIT, REVIEW_CACHE_NAMESPACE, REVIEW_CACHE_TIMEOUT
from brainzutils import cache

recording_bp = Blueprint('ws_recording', __name__)

@recording_bp.route('/<uuid:recording_mbid>', methods=['GET', 'OPTIONS'])
@crossdomain(headers="Authorization, Content-Type")
def recording_entity_handler(recording_mbid):
    """Get list of reviews.

    **Request Example:**

    .. code-block:: bash

        $ curl "https://critiquebrainz.org/ws/1/recording/299e8f6d-957d-43fd-a724-ebfd4c570bbc" \\
                -X GET

    **Response Example:**

    .. code-block:: json

    {
        "average_rating": 5.0,
        "latest_reviews": [
            {
                "created": "Sat, 04 Dec 2021 13:17:15 GMT",
                "edits": 0,
                "entity_id": "299e8f6d-957d-43fd-a724-ebfd4c570bbc",
                "entity_type": "recording",
                "full_name": "Creative Commons Attribution-ShareAlike 3.0 Unported",
                "id": "5f98882a-86c0-41b6-b828-59c3886adf6b",
                "info_url": "https://creativecommons.org/licenses/by-sa/3.0/",
                "is_draft": false,
                "is_hidden": false,
                "language": "en",
                "last_revision": {
                    "id": 11177,
                    "rating": 5,
                    "review_id": "5f98882a-86c0-41b6-b828-59c3886adf6b",
                    "text": null,
                    "timestamp": "Sat, 04 Dec 2021 13:17:15 GMT"
                },
                "last_updated": "Sat, 04 Dec 2021 13:17:15 GMT",
                "license_id": "CC BY-SA 3.0",
                "popularity": 0,
                "published_on": "Sat, 04 Dec 2021 13:17:15 GMT",
                "rating": 5,
                "source": null,
                "source_url": null,
                "text": null,
                "user": {
                    "created": "Wed, 26 May 2021 13:20:30 GMT",
                    "display_name": "akshaaatt",
                    "id": "7a98bc0a-1e40-4cd6-b36d-8c25931533af",
                    "karma": 1,
                    "user_type": "Noob"
                },
                "votes_negative_count": 0,
                "votes_positive_count": 0
            }
        ],
        "ratings_stats": {
            "1": 0,
            "2": 0,
            "3": 0,
            "4": 0,
            "5": 1
        },
        "recording": {
            "artist-credit-phrase": "Linkin Park",
            "artists": [
                {
                    "mbid": "f59c5520-5f46-4d2c-b2c4-822eabf53419",
                    "name": "Linkin Park"
                }
            ],
            "comment": "live, 2012-06-05: Admiralspalast, Berlin, Germany",
            "length": 301.0,
            "mbid": "299e8f6d-957d-43fd-a724-ebfd4c570bbc",
            "name": "New Divide",
            "rating": 100,
            "video": true
        },
        "reviews_count": 1,
        "top_reviews": [
            {
                "created": "Sat, 04 Dec 2021 13:17:15 GMT",
                "edits": 0,
                "entity_id": "299e8f6d-957d-43fd-a724-ebfd4c570bbc",
                "entity_type": "recording",
                "full_name": "Creative Commons Attribution-ShareAlike 3.0 Unported",
                "id": "5f98882a-86c0-41b6-b828-59c3886adf6b",
                "info_url": "https://creativecommons.org/licenses/by-sa/3.0/",
                "is_draft": false,
                "is_hidden": false,
                "language": "en",
                "last_revision": {
                    "id": 11177,
                    "rating": 5,
                    "review_id": "5f98882a-86c0-41b6-b828-59c3886adf6b",
                    "text": null,
                    "timestamp": "Sat, 04 Dec 2021 13:17:15 GMT"
                },
                "last_updated": "Sat, 04 Dec 2021 13:17:15 GMT",
                "license_id": "CC BY-SA 3.0",
                "popularity": 0,
                "published_on": "Sat, 04 Dec 2021 13:17:15 GMT",
                "rating": 5,
                "source": null,
                "source_url": null,
                "text": null,
                "user": {
                    "created": "Wed, 26 May 2021 13:20:30 GMT",
                    "display_name": "akshaaatt",
                    "id": "7a98bc0a-1e40-4cd6-b36d-8c25931533af",
                    "karma": 1,
                    "user_type": "Noob"
                },
                "votes_negative_count": 0,
                "votes_positive_count": 0
            }
        ]
    }

    :statuscode 200: no error
    :statuscode 404: recording not found

    :resheader Content-Type: *application/json*
    """

    recording = db_recording.get_recording_by_mbid(str(recording_mbid))

    if not recording:
        raise NotFound("Can't find a recording with ID: {recording_mbid}".format(recording_mbid=recording_mbid))

    user_review = None

    user_id = Parser.uuid('uri', 'user_id', optional=True)
    if user_id:
        user_review_cache_key = cache.gen_key('entity_api', recording['mbid'], user_id, "user_review")
        user_review = cache.get(user_review_cache_key)
        if not user_review:
            user_review, _ = db_review.list_reviews(
                entity_id=recording['mbid'],
                entity_type='recording',
                user_id=user_id
            )
            if user_review:
                user_review = db_review.to_dict(user_review[0])
            else:
                user_review = None

            cache.set(user_review_cache_key, user_review,
                      expirein=REVIEW_CACHE_TIMEOUT, namespace=REVIEW_CACHE_NAMESPACE)

    ratings_stats, average_rating = db_rating_stats.get_stats(recording_mbid, "recording")

    top_reviews_cache_key = cache.gen_key("entity_api_recording", recording['mbid'], "top_reviews")
    top_reviews_cached_result = cache.get(top_reviews_cache_key, REVIEW_CACHE_NAMESPACE)

    if top_reviews_cached_result:
        top_reviews, reviews_count = top_reviews_cached_result
    else:
        top_reviews, reviews_count = db_review.list_reviews(
            entity_id=recording['mbid'],
            entity_type='recording',
            sort='popularity',
            limit=REVIEWS_LIMIT,
            offset=0,
        )
        top_reviews = [db_review.to_dict(review) for review in top_reviews]

        cache.set(top_reviews_cache_key, (top_reviews, reviews_count),
                  expirein=REVIEW_CACHE_TIMEOUT, namespace=REVIEW_CACHE_NAMESPACE)

    latest_reviews_cache_key = cache.gen_key("entity_api_recording", recording['mbid'], "latest_reviews")
    latest_reviews_cached_result = cache.get(latest_reviews_cache_key, REVIEW_CACHE_NAMESPACE)

    if latest_reviews_cached_result:
        latest_reviews, reviews_count = latest_reviews_cached_result
    else:
        latest_reviews, reviews_count = db_review.list_reviews(
            entity_id=recording['mbid'],
            entity_type='recording',
            sort='published_on',
            limit=REVIEWS_LIMIT,
            offset=0,
        )
        latest_reviews = [db_review.to_dict(review) for review in latest_reviews]

        cache.set(latest_reviews_cache_key, (latest_reviews, reviews_count),
                  expirein=REVIEW_CACHE_TIMEOUT, namespace=REVIEW_CACHE_NAMESPACE)

    result = {
        "recording": recording,
        "average_rating": average_rating,
        "ratings_stats": ratings_stats,
        "reviews_count": reviews_count,
        "top_reviews": top_reviews,
        "latest_reviews": latest_reviews
    }
    if user_id:
        result['user_review'] = user_review

    return jsonify(**result)
