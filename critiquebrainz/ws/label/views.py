from flask import Blueprint, jsonify
import critiquebrainz.db.review as db_review
import critiquebrainz.db.users as db_users
import critiquebrainz.db.rating_stats as db_rating_stats
from critiquebrainz.frontend.external.musicbrainz_db import label as db_label
from critiquebrainz.decorators import crossdomain
from critiquebrainz.ws.exceptions import NotFound
from critiquebrainz.ws.parser import Parser
from critiquebrainz.ws import REVIEWS_LIMIT
from critiquebrainz.ws import REVIEWS_LIMIT, REVIEW_CACHE_NAMESPACE, REVIEW_CACHE_TIMEOUT
from brainzutils import cache

label_bp = Blueprint('ws_label', __name__)


@label_bp.route('/<uuid:label_mbid>', methods=['GET', 'OPTIONS'])
@crossdomain(headers="Authorization, Content-Type")
def label_entity_handler(label_mbid):
    """Get list of reviews.

    **Request Example:**

    .. code-block:: bash

        $ curl "https://critiquebrainz.org/ws/1/label/e268deeb-31bc-4428-9caf-c7e2726cd496" \\
                -X GET

    **Response Example:**

    .. code-block:: json

    {
        "average_rating": 5.0,
        "label": {
            "area": "Dakar",
            "artist-rels": [
                {
                    "artist": {
                        "comment": "Songwriter / Producer / CEO",
                        "life-span": {
                            "begin": "1992-06-07"
                        },
                        "mbid": "547bb51b-a016-402e-8120-50c3e8def75b",
                        "name": "Med Mouha",
                        "sort_name": "Mouha, Med",
                        "type": "Person"
                    },
                    "begin-year": 2019,
                    "direction": "backward",
                    "end-year": null,
                    "type": "label founder",
                    "type-id": "577996f3-7ff9-45cf-877e-740fb1267a63"
                }
            ],
            "comment": "Records, Dabass",
            "external-urls": [
                {
                    "begin-year": null,
                    "direction": "forward",
                    "end-year": null,
                    "icon": "discogs-16.png",
                    "name": "Discogs",
                    "type": "discogs",
                    "type-id": "5b987f87-25bc-4a2d-b3f1-3618795b8207",
                    "url": {
                        "mbid": "e810e5d5-d2cc-406a-9365-a2bc84e35754",
                        "url": "https://www.discogs.com/label/2385910"
                    }
                }
            ],
            "life-span": {
                "begin": "2019"
            },
            "mbid": "e268deeb-31bc-4428-9caf-c7e2726cd496",
            "name": "Dabass Records",
            "rating": 100,
            "type": "Production"
        },
        "latest_reviews": [
            {
                "created": "Sun, 05 Sep 2021 16:57:39 GMT",
                "edits": 0,
                "entity_id": "e268deeb-31bc-4428-9caf-c7e2726cd496",
                "entity_type": "label",
                "full_name": "Creative Commons Attribution-ShareAlike 3.0 Unported",
                "id": "5d941575-29ff-4dde-a48a-ad0ba5daec8c",
                "info_url": "https://creativecommons.org/licenses/by-sa/3.0/",
                "is_draft": false,
                "is_hidden": false,
                "language": "en",
                "last_revision": {
                    "id": 10991,
                    "rating": 5,
                    "review_id": "5d941575-29ff-4dde-a48a-ad0ba5daec8c",
                    "text": null,
                    "timestamp": "Sun, 05 Sep 2021 16:57:39 GMT"
                },
                "last_updated": "Sun, 05 Sep 2021 16:57:39 GMT",
                "license_id": "CC BY-SA 3.0",
                "popularity": 0,
                "published_on": "Sun, 05 Sep 2021 16:57:39 GMT",
                "rating": 5,
                "source": null,
                "source_url": null,
                "text": null,
                "user": {
                    "created": "Sun, 05 Sep 2021 14:20:33 GMT",
                    "display_name": "Medmouha",
                    "id": "20d9fb34-dc1f-4aa4-8082-c69e4b20f660",
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
                "created": "Sun, 05 Sep 2021 16:57:39 GMT",
                "edits": 0,
                "entity_id": "e268deeb-31bc-4428-9caf-c7e2726cd496",
                "entity_type": "label",
                "full_name": "Creative Commons Attribution-ShareAlike 3.0 Unported",
                "id": "5d941575-29ff-4dde-a48a-ad0ba5daec8c",
                "info_url": "https://creativecommons.org/licenses/by-sa/3.0/",
                "is_draft": false,
                "is_hidden": false,
                "language": "en",
                "last_revision": {
                    "id": 10991,
                    "rating": 5,
                    "review_id": "5d941575-29ff-4dde-a48a-ad0ba5daec8c",
                    "text": null,
                    "timestamp": "Sun, 05 Sep 2021 16:57:39 GMT"
                },
                "last_updated": "Sun, 05 Sep 2021 16:57:39 GMT",
                "license_id": "CC BY-SA 3.0",
                "popularity": 0,
                "published_on": "Sun, 05 Sep 2021 16:57:39 GMT",
                "rating": 5,
                "source": null,
                "source_url": null,
                "text": null,
                "user": {
                    "created": "Sun, 05 Sep 2021 14:20:33 GMT",
                    "display_name": "Medmouha",
                    "id": "20d9fb34-dc1f-4aa4-8082-c69e4b20f660",
                    "karma": 0,
                    "user_type": "Noob"
                },
                "votes_negative_count": 0,
                "votes_positive_count": 0
            }
        ]
    }

    :statuscode 200: no error
    :statuscode 404: label not found

    :query username: User's username **(optional)**

    :resheader Content-Type: *application/json*
    """

    label = db_label.get_label_by_mbid(str(label_mbid))

    if not label:
        raise NotFound("Can't find a label with ID: {label_mbid}".format(label_mbid=label_mbid))

    user_review = None

    username = Parser.string('uri', 'username', optional=True)
    if username:
        user_review_cache_key = cache.gen_key('entity_api', label['mbid'], username, "user_review")
        user_review = cache.get(user_review_cache_key)
        if not user_review:
            user = db_users.get_by_mbid(username)
            if user:
                user_id = user['id']

                user_review, _ = db_review.list_reviews(
                    entity_id=label['mbid'],
                    entity_type='label',
                    user_id=user_id
                )
                if user_review:
                    user_review = db_review.to_dict(user_review[0])

                cache.set(user_review_cache_key, user_review,
                        expirein=REVIEW_CACHE_TIMEOUT, namespace=REVIEW_CACHE_NAMESPACE)

            else:
                user_review = []

    ratings_stats, average_rating = db_rating_stats.get_stats(label_mbid, "label")

    top_reviews_cache_key = cache.gen_key("entity_api_label", label['mbid'], "top_reviews")
    top_reviews_cached_result = cache.get(top_reviews_cache_key, REVIEW_CACHE_NAMESPACE)

    if top_reviews_cached_result:
        top_reviews, reviews_count = top_reviews_cached_result
    else:
        top_reviews, reviews_count = db_review.list_reviews(
            entity_id=label['mbid'],
            entity_type='label',
            sort='popularity',
            limit=REVIEWS_LIMIT,
            offset=0,
        )
        top_reviews = [db_review.to_dict(review) for review in top_reviews]

        cache.set(top_reviews_cache_key, (top_reviews, reviews_count),
                  expirein=REVIEW_CACHE_TIMEOUT, namespace=REVIEW_CACHE_NAMESPACE)

    latest_reviews_cache_key = cache.gen_key("entity_api_label", label['mbid'], "latest_reviews")
    latest_reviews_cached_result = cache.get(latest_reviews_cache_key, REVIEW_CACHE_NAMESPACE)

    if latest_reviews_cached_result:
        latest_reviews, reviews_count = latest_reviews_cached_result
    else:
        latest_reviews, reviews_count = db_review.list_reviews(
            entity_id=label['mbid'],
            entity_type='label',
            sort='published_on',
            limit=REVIEWS_LIMIT,
            offset=0,
        )
        latest_reviews = [db_review.to_dict(review) for review in latest_reviews]

        cache.set(latest_reviews_cache_key, (latest_reviews, reviews_count),
                  expirein=REVIEW_CACHE_TIMEOUT, namespace=REVIEW_CACHE_NAMESPACE)

    result = {
        "label": label,
        "average_rating": average_rating,
        "ratings_stats": ratings_stats,
        "reviews_count": reviews_count,
        "top_reviews": top_reviews,
        "latest_reviews": latest_reviews
    }

    if username:
        result['user_review'] = user_review

    return jsonify(**result)
