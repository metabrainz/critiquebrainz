from flask import Blueprint, jsonify
import critiquebrainz.db.review as db_review
import critiquebrainz.db.users as db_users
import critiquebrainz.db.rating_stats as db_rating_stats
from critiquebrainz.frontend.external.bookbrainz_db import author as db_author
from critiquebrainz.decorators import crossdomain
from critiquebrainz.ws.exceptions import NotFound
from critiquebrainz.ws.parser import Parser
from critiquebrainz.ws import REVIEWS_LIMIT, REVIEW_CACHE_NAMESPACE, REVIEW_CACHE_TIMEOUT
from brainzutils import cache

author_bp = Blueprint('ws_author', __name__)


@author_bp.route('/<uuid:author_bbid>', methods=['GET', 'OPTIONS'])
@crossdomain(headers="Authorization, Content-Type")
def author_entity_handler(author_bbid):
    """Get list of reviews.

    **Request Example:**

    .. code-block:: bash

        $ curl "https://critiquebrainz.org/ws/1/author/e5c4e68b-bfce-4c77-9ca2-0f0a2d4d09f0" \\
                -X GET

    **Response Example:**

    .. code-block:: json

    {
        "author": {
            "area_id": null,
            "area_info": [],
            "author_type": "Person",
            "bbid": "e5c4e68b-bfce-4c77-9ca2-0f0a2d4d09f0",
            "begin_area_id": 221,
            "begin_day": 31,
            "begin_month": 7,
            "begin_year": 1965,
            "disambiguation": null,
            "end_area_id": null,
            "end_day": null,
            "end_month": null,
            "end_year": null,
            "ended": false,
            "gender": "Female",
            "identifier_set_id": 7401,
            "identifiers": [
                {
                    "icon": "wikidata-16.png",
                    "name": "Wikidata ID",
                    "url": "https://www.wikidata.org/wiki/Q34660",
                    "value": "Q34660"
                },
                {
                    "icon": "viaf-16.png",
                    "name": "VIAF",
                    "url": "https://viaf.org/viaf/116796842",
                    "value": "116796842"
                },
                {
                    "icon": "wikidata-16.png",
                    "name": "Wikidata ID",
                    "url": "https://www.wikidata.org/wiki/Q1190608",
                    "value": "Q1190608"
                }
            ],
            "name": "J. K. Rowling",
            "relationship_set_id": 151715,
            "sort_name": "Rowling, J. K."
        },
        "average_rating": 5.0,
        "latest_reviews": [
            {
                "created": "Tue, 16 Aug 2022 11:25:44 GMT",
                "edits": 0,
                "entity_id": "e5c4e68b-bfce-4c77-9ca2-0f0a2d4d09f0",
                "entity_type": "bb_author",
                "full_name": "Creative Commons Attribution-ShareAlike 3.0 Unported",
                "id": "326e702a-020f-40e7-b369-9142a7af4315",
                "info_url": "https://creativecommons.org/licenses/by-sa/3.0/",
                "is_draft": false,
                "is_hidden": false,
                "language": "en",
                "last_revision": {
                    "id": 11785,
                    "rating": 5,
                    "review_id": "326e702a-020f-40e7-b369-9142a7af4315",
                    "text": null,
                    "timestamp": "Fri, 02 Sep 2022 09:54:13 GMT"
                },
                "last_updated": "Fri, 02 Sep 2022 09:54:13 GMT",
                "license_id": "CC BY-SA 3.0",
                "popularity": 0,
                "published_on": "Tue, 16 Aug 2022 11:25:44 GMT",
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
                "created": "Tue, 16 Aug 2022 11:25:44 GMT",
                "edits": 0,
                "entity_id": "e5c4e68b-bfce-4c77-9ca2-0f0a2d4d09f0",
                "entity_type": "bb_author",
                "full_name": "Creative Commons Attribution-ShareAlike 3.0 Unported",
                "id": "326e702a-020f-40e7-b369-9142a7af4315",
                "info_url": "https://creativecommons.org/licenses/by-sa/3.0/",
                "is_draft": false,
                "is_hidden": false,
                "language": "en",
                "last_revision": {
                    "id": 11785,
                    "rating": 5,
                    "review_id": "326e702a-020f-40e7-b369-9142a7af4315",
                    "text": null,
                    "timestamp": "Fri, 02 Sep 2022 09:54:13 GMT"
                },
                "last_updated": "Fri, 02 Sep 2022 09:54:13 GMT",
                "license_id": "CC BY-SA 3.0",
                "popularity": 0,
                "published_on": "Tue, 16 Aug 2022 11:25:44 GMT",
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
    :statuscode 404: author not found

    :query username: User's username **(optional)**

    :resheader Content-Type: *application/json*
    """

    author = db_author.get_author_by_bbid(str(author_bbid))

    if not author:
        raise NotFound("Can't find an author with ID: {author_bbid}".format(author_bbid=author_bbid))

    user_review = []

    username = Parser.string('uri', 'username', optional=True)
    if username:
        user_review_cache_key = cache.gen_key('entity_api', author['bbid'], username, "user_review")
        user_review = cache.get(user_review_cache_key, namespace=REVIEW_CACHE_NAMESPACE)
        if not user_review:
            user = db_users.get_by_mbid(username)
            if user:
                user_id = user['id']

                user_review, _ = db_review.list_reviews(
                    entity_id=author['bbid'],
                    entity_type='bb_author',
                    user_id=user_id
                )
                if user_review:
                    user_review = db_review.to_dict(user_review[0])

                cache.set(user_review_cache_key, user_review,
                        expirein=REVIEW_CACHE_TIMEOUT, namespace=REVIEW_CACHE_NAMESPACE)

            else:
                user_review = []


    ratings_stats, average_rating = db_rating_stats.get_stats(author_bbid, "bb_author")

    top_reviews_cache_key = cache.gen_key("entity_api_bb_author", author['bbid'], "top_reviews")
    top_reviews_cached_result = cache.get(top_reviews_cache_key, REVIEW_CACHE_NAMESPACE)

    if top_reviews_cached_result:
        top_reviews, reviews_count = top_reviews_cached_result
    else:
        top_reviews, reviews_count = db_review.list_reviews(
            entity_id=author['bbid'],
            entity_type='bb_author',
            sort='popularity',
            limit=REVIEWS_LIMIT,
            offset=0,
        )
        top_reviews = [db_review.to_dict(review) for review in top_reviews]

        cache.set(top_reviews_cache_key, (top_reviews, reviews_count),
                  expirein=REVIEW_CACHE_TIMEOUT, namespace=REVIEW_CACHE_NAMESPACE)

    latest_reviews_cache_key = cache.gen_key("entity_api_bb_author", author['bbid'], "latest_reviews")
    latest_reviews_cached_result = cache.get(latest_reviews_cache_key, REVIEW_CACHE_NAMESPACE)

    if latest_reviews_cached_result:
        latest_reviews, reviews_count = latest_reviews_cached_result
    else:
        latest_reviews, reviews_count = db_review.list_reviews(
            entity_id=author['bbid'],
            entity_type='bb_author',
            sort='published_on',
            limit=REVIEWS_LIMIT,
            offset=0,
        )
        latest_reviews = [db_review.to_dict(review) for review in latest_reviews]

        cache.set(latest_reviews_cache_key, (latest_reviews, reviews_count),
                  expirein=REVIEW_CACHE_TIMEOUT, namespace=REVIEW_CACHE_NAMESPACE)

    result = {
        "author": author,
        "average_rating": average_rating,
        "ratings_stats": ratings_stats,
        "reviews_count": reviews_count,
        "top_reviews": top_reviews,
        "latest_reviews": latest_reviews
    }
    if username:
        result['user_review'] = user_review

    return jsonify(**result)
