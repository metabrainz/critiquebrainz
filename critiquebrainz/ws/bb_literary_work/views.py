from flask import Blueprint, jsonify
import critiquebrainz.db.review as db_review
import critiquebrainz.db.rating_stats as db_rating_stats
from critiquebrainz.frontend.external.bookbrainz_db import literary_work as db_literary_work
from critiquebrainz.decorators import crossdomain
from critiquebrainz.ws.exceptions import NotFound
from critiquebrainz.ws.parser import Parser
from critiquebrainz.ws import REVIEWS_LIMIT, REVIEW_CACHE_NAMESPACE, REVIEW_CACHE_TIMEOUT
from brainzutils import cache

literary_work_bp = Blueprint('ws_literary_work', __name__)


@literary_work_bp.route('/<uuid:literary_work_bbid>', methods=['GET', 'OPTIONS'])
@crossdomain(headers="Authorization, Content-Type")
def literary_work_entity_handler(literary_work_bbid):
    """Get list of reviews.

    **Request Example:**

    .. code-block:: bash

        $ curl "https://critiquebrainz.org/ws/1/literary-work/b2d19b45-117d-437d-b55b-7fff01e29603" \\
                -X GET

    **Response Example:**

    .. code-block:: json

    {
        "average_rating": 5.0,
        "latest_reviews": [
            {
                "created": "Thu, 18 Aug 2022 09:21:37 GMT",
                "edits": 0,
                "entity_id": "b2d19b45-117d-437d-b55b-7fff01e29603",
                "entity_type": "bb_literary_work",
                "full_name": "Creative Commons Attribution-ShareAlike 3.0 Unported",
                "id": "178b5ef1-ec96-40b8-a08c-b11b01550efd",
                "info_url": "https://creativecommons.org/licenses/by-sa/3.0/",
                "is_draft": false,
                "is_hidden": false,
                "language": "en",
                "last_revision": {
                    "id": 11775,
                    "rating": 5,
                    "review_id": "178b5ef1-ec96-40b8-a08c-b11b01550efd",
                    "text": null,
                    "timestamp": "Thu, 18 Aug 2022 09:21:37 GMT"
                },
                "last_updated": "Thu, 18 Aug 2022 09:21:37 GMT",
                "license_id": "CC BY-SA 3.0",
                "popularity": 0,
                "published_on": "Thu, 18 Aug 2022 09:21:37 GMT",
                "rating": 5,
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
        "literary_work": {
            "bbid": "b2d19b45-117d-437d-b55b-7fff01e29603",
            "disambiguation": null,
            "identifier_set_id": 2831,
            "identifiers": [
                {
                    "icon": "wikidata-16.png",
                    "name": "Wikidata ID",
                    "url": "https://www.wikidata.org/wiki/Q47209",
                    "value": "Q47209"
                },
                {
                    "icon": "viaf-16.png",
                    "name": "VIAF",
                    "url": "https://viaf.org/viaf/190455963",
                    "value": "190455963"
                },
                {
                    "icon": null,
                    "name": "OpenLibrary Work ID",
                    "url": "https://openlibrary.org/works/OL16313124W",
                    "value": "OL16313124W"
                },
                {
                    "icon": null,
                    "name": "OpenLibrary Work ID",
                    "url": "https://openlibrary.org/works/OL16313123W",
                    "value": "OL16313123W"
                }
            ],
            "languages": [
                "English"
            ],
            "name": "Harry Potter and the Chamber of Secrets",
            "relationship_set_id": 136021,
            "rels": null,
            "sort_name": "Chamber of Secrets, Harry Potter and the",
            "work_type": "Novel"
        },
        "ratings_stats": {
            "1": 0,
            "2": 0,
            "3": 0,
            "4": 0,
            "5": 1
        },
        "reviews_count": 1,
        "top_reviews": [
            {
                "created": "Thu, 18 Aug 2022 09:21:37 GMT",
                "edits": 0,
                "entity_id": "b2d19b45-117d-437d-b55b-7fff01e29603",
                "entity_type": "bb_literary_work",
                "full_name": "Creative Commons Attribution-ShareAlike 3.0 Unported",
                "id": "178b5ef1-ec96-40b8-a08c-b11b01550efd",
                "info_url": "https://creativecommons.org/licenses/by-sa/3.0/",
                "is_draft": false,
                "is_hidden": false,
                "language": "en",
                "last_revision": {
                    "id": 11775,
                    "rating": 5,
                    "review_id": "178b5ef1-ec96-40b8-a08c-b11b01550efd",
                    "text": null,
                    "timestamp": "Thu, 18 Aug 2022 09:21:37 GMT"
                },
                "last_updated": "Thu, 18 Aug 2022 09:21:37 GMT",
                "license_id": "CC BY-SA 3.0",
                "popularity": 0,
                "published_on": "Thu, 18 Aug 2022 09:21:37 GMT",
                "rating": 5,
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
    :statuscode 404: literary work not found

    :resheader Content-Type: *application/json*
    """

    literary_work = db_literary_work.get_literary_work_by_bbid(str(literary_work_bbid))

    if not literary_work:
        raise NotFound("Can't find a literary_work with ID: {literary_work_bbid}".format(literary_work_bbid=literary_work_bbid))

    user_review = []

    user_id = Parser.uuid('uri', 'user_id', optional=True)
    if user_id:
        user_review_cache_key = cache.gen_key('entity_api', literary_work['bbid'], user_id, "user_review")
        user_review = cache.get(user_review_cache_key)
        if not user_review:
            user_review, _ = db_review.list_reviews(
                entity_id=literary_work['bbid'],
                entity_type='bb_literary_work',
                user_id=user_id
            )
            if user_review:
                user_review = db_review.to_dict(user_review[0])
            else:
                user_review = []

            cache.set(user_review_cache_key, user_review,
                      expirein=REVIEW_CACHE_TIMEOUT, namespace=REVIEW_CACHE_NAMESPACE)

    ratings_stats, average_rating = db_rating_stats.get_stats(literary_work_bbid, "bb_literary_work")

    top_reviews_cache_key = cache.gen_key("entity_api_bb_literary_work", literary_work['bbid'], "top_reviews")
    top_reviews_cached_result = cache.get(top_reviews_cache_key, REVIEW_CACHE_NAMESPACE)

    if top_reviews_cached_result:
        top_reviews, reviews_count = top_reviews_cached_result
    else:
        top_reviews, reviews_count = db_review.list_reviews(
            entity_id=literary_work['bbid'],
            entity_type='bb_literary_work',
            sort='popularity',
            limit=REVIEWS_LIMIT,
            offset=0,
        )
        top_reviews = [db_review.to_dict(review) for review in top_reviews]

        cache.set(top_reviews_cache_key, (top_reviews, reviews_count),
                  expirein=REVIEW_CACHE_TIMEOUT, namespace=REVIEW_CACHE_NAMESPACE)

    latest_reviews_cache_key = cache.gen_key("entity_api_bb_literary_work", literary_work['bbid'], "latest_reviews")
    latest_reviews_cached_result = cache.get(latest_reviews_cache_key, REVIEW_CACHE_NAMESPACE)

    if latest_reviews_cached_result:
        latest_reviews, reviews_count = latest_reviews_cached_result
    else:
        latest_reviews, reviews_count = db_review.list_reviews(
            entity_id=literary_work['bbid'],
            entity_type='bb_literary_work',
            sort='published_on',
            limit=REVIEWS_LIMIT,
            offset=0,
        )
        latest_reviews = [db_review.to_dict(review) for review in latest_reviews]

        cache.set(latest_reviews_cache_key, (latest_reviews, reviews_count),
                  expirein=REVIEW_CACHE_TIMEOUT, namespace=REVIEW_CACHE_NAMESPACE)

    result = {
        "literary_work": literary_work,
        "average_rating": average_rating,
        "ratings_stats": ratings_stats,
        "reviews_count": reviews_count,
        "top_reviews": top_reviews,
        "latest_reviews": latest_reviews
    }
    if user_id:
        result['user_review'] = user_review

    return jsonify(**result)
