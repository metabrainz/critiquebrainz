from flask import Blueprint, jsonify
import critiquebrainz.db.review as db_review
import critiquebrainz.db.users as db_users
import critiquebrainz.db.rating_stats as db_rating_stats
from critiquebrainz.frontend.external.bookbrainz_db import series as db_series
from critiquebrainz.decorators import crossdomain
from critiquebrainz.ws.exceptions import NotFound
from critiquebrainz.ws.parser import Parser
from critiquebrainz.ws import REVIEWS_LIMIT, REVIEW_CACHE_NAMESPACE, REVIEW_CACHE_TIMEOUT
from brainzutils import cache

series_bp = Blueprint('ws_series', __name__)


@series_bp.route('/<uuid:series_bbid>', methods=['GET', 'OPTIONS'])
@crossdomain(headers="Authorization, Content-Type")
def series_entity_handler(series_bbid):
    """Get list of reviews.

    **Request Example:**

    .. code-block:: bash

        $ curl "https://critiquebrainz.org/ws/1/series/e6f48cbd-26de-4c2e-a24a-29892f9eb3be" \\
                -X GET

    **Response Example:**

    .. code-block:: json

    {
        "average_rating": 4.0,
        "latest_reviews": [
            {
                "created": "Tue, 16 Aug 2022 11:26:58 GMT",
                "edits": 0,
                "entity_id": "e6f48cbd-26de-4c2e-a24a-29892f9eb3be",
                "entity_type": "bb_series",
                "full_name": "Creative Commons Attribution-ShareAlike 3.0 Unported",
                "id": "998512d8-0d6b-4c76-bfb7-0ec666e3fa0a",
                "info_url": "https://creativecommons.org/licenses/by-sa/3.0/",
                "is_draft": false,
                "is_hidden": false,
                "language": "en",
                "last_revision": {
                    "id": 11773,
                    "rating": 4,
                    "review_id": "998512d8-0d6b-4c76-bfb7-0ec666e3fa0a",
                    "text": null,
                    "timestamp": "Tue, 16 Aug 2022 11:26:58 GMT"
                },
                "last_updated": "Tue, 16 Aug 2022 11:26:58 GMT",
                "license_id": "CC BY-SA 3.0",
                "popularity": 0,
                "published_on": "Tue, 16 Aug 2022 11:26:58 GMT",
                "rating": 4,
                "source": null,
                "source_url": null,
                "text": null,
                "user": {
                    "created": "Tue, 18 Jan 2022 09:53:49 GMT",
                    "display_name": "Ansh Goyal",
                    "id": "11a1160e-d607-4882-8a82-e2e800f664fe",
                    "karma": 0,
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
            "4": 1,
            "5": 0
        },
        "reviews_count": 1,
        "series": {
            "bbid": "e6f48cbd-26de-4c2e-a24a-29892f9eb3be",
            "disambiguation": "English",
            "identifier_set_id": null,
            "identifiers": null,
            "name": "Harry Potter",
            "relationship_set_id": 151767,
            "series_ordering_type": "Automatic",
            "series_type": "Work",
            "sort_name": "Harry Potter"
        },
        "top_reviews": [
            {
                "created": "Tue, 16 Aug 2022 11:26:58 GMT",
                "edits": 0,
                "entity_id": "e6f48cbd-26de-4c2e-a24a-29892f9eb3be",
                "entity_type": "bb_series",
                "full_name": "Creative Commons Attribution-ShareAlike 3.0 Unported",
                "id": "998512d8-0d6b-4c76-bfb7-0ec666e3fa0a",
                "info_url": "https://creativecommons.org/licenses/by-sa/3.0/",
                "is_draft": false,
                "is_hidden": false,
                "language": "en",
                "last_revision": {
                    "id": 11773,
                    "rating": 4,
                    "review_id": "998512d8-0d6b-4c76-bfb7-0ec666e3fa0a",
                    "text": null,
                    "timestamp": "Tue, 16 Aug 2022 11:26:58 GMT"
                },
                "last_updated": "Tue, 16 Aug 2022 11:26:58 GMT",
                "license_id": "CC BY-SA 3.0",
                "popularity": 0,
                "published_on": "Tue, 16 Aug 2022 11:26:58 GMT",
                "rating": 4,
                "source": null,
                "source_url": null,
                "text": null,
                "user": {
                    "created": "Tue, 18 Jan 2022 09:53:49 GMT",
                    "display_name": "Ansh Goyal",
                    "id": "11a1160e-d607-4882-8a82-e2e800f664fe",
                    "karma": 0,
                    "user_type": "Noob"
                },
                "votes_negative_count": 0,
                "votes_positive_count": 0
            }
        ]
    }

    :statuscode 200: no error
    :statuscode 404: series not found

    :query username: User's username **(optional)**

    :resheader Content-Type: *application/json*
    """

    series = db_series.get_series_by_bbid(str(series_bbid))

    if not series:
        raise NotFound("Can't find a series with ID: {series_bbid}".format(series_bbid=series_bbid))

    user_review = []

    username = Parser.string('uri', 'username', optional=True)
    if username:
        user_review_cache_key = cache.gen_key('entity_api', series['bbid'], username, "user_review")
        user_review = cache.get(user_review_cache_key, REVIEW_CACHE_NAMESPACE)
        if not user_review:
            user = db_users.get_by_mbid(username)
            if user:
                user_id = user['id']

                user_review, _ = db_review.list_reviews(
                    entity_id=series['bbid'],
                    entity_type='bb_series',
                    user_id=user_id
                )
                if user_review:
                    user_review = db_review.to_dict(user_review[0])

                cache.set(user_review_cache_key, user_review,
                        expirein=REVIEW_CACHE_TIMEOUT, namespace=REVIEW_CACHE_NAMESPACE)

            else:
                user_review = []


    ratings_stats, average_rating = db_rating_stats.get_stats(series_bbid, "bb_series")

    top_reviews_cache_key = cache.gen_key("entity_api_bb_series", series['bbid'], "top_reviews")
    top_reviews_cached_result = cache.get(top_reviews_cache_key, REVIEW_CACHE_NAMESPACE)

    if top_reviews_cached_result:
        top_reviews, reviews_count = top_reviews_cached_result
    else:
        top_reviews, reviews_count = db_review.list_reviews(
            entity_id=series['bbid'],
            entity_type='bb_series',
            sort='popularity',
            limit=REVIEWS_LIMIT,
            offset=0,
        )
        top_reviews = [db_review.to_dict(review) for review in top_reviews]

        cache.set(top_reviews_cache_key, (top_reviews, reviews_count),
                  expirein=REVIEW_CACHE_TIMEOUT, namespace=REVIEW_CACHE_NAMESPACE)

    latest_reviews_cache_key = cache.gen_key("entity_api_bb_series", series['bbid'], "latest_reviews")
    latest_reviews_cached_result = cache.get(latest_reviews_cache_key, REVIEW_CACHE_NAMESPACE)

    if latest_reviews_cached_result:
        latest_reviews, reviews_count = latest_reviews_cached_result
    else:
        latest_reviews, reviews_count = db_review.list_reviews(
            entity_id=series['bbid'],
            entity_type='bb_series',
            sort='published_on',
            limit=REVIEWS_LIMIT,
            offset=0,
        )
        latest_reviews = [db_review.to_dict(review) for review in latest_reviews]

        cache.set(latest_reviews_cache_key, (latest_reviews, reviews_count),
                  expirein=REVIEW_CACHE_TIMEOUT, namespace=REVIEW_CACHE_NAMESPACE)

    result = {
        "series": series,
        "average_rating": average_rating,
        "ratings_stats": ratings_stats,
        "reviews_count": reviews_count,
        "top_reviews": top_reviews,
        "latest_reviews": latest_reviews
    }

    if username:
        result['user_review'] = user_review

    return jsonify(**result)
