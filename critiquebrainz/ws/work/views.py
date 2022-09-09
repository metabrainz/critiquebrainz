from flask import Blueprint, jsonify
import critiquebrainz.db.review as db_review
import critiquebrainz.db.users as db_users
import critiquebrainz.db.rating_stats as db_rating_stats
from critiquebrainz.frontend.external.musicbrainz_db import work as db_work
from critiquebrainz.decorators import crossdomain
from critiquebrainz.ws.exceptions import NotFound
from critiquebrainz.ws.parser import Parser
from critiquebrainz.ws import REVIEWS_LIMIT, REVIEW_CACHE_NAMESPACE, REVIEW_CACHE_TIMEOUT
from brainzutils import cache


work_bp = Blueprint('ws_work', __name__)


@work_bp.route('/<uuid:work_mbid>', methods=['GET', 'OPTIONS'])
@crossdomain(headers="Authorization, Content-Type")
def work_entity_handler(work_mbid):
    """Get list of reviews.

    **Request Example:**

    .. code-block:: bash

        $ curl "https://critiquebrainz.org/ws/1/work/233d58f7-aba4-405a-8cd3-4adb344bd333" \\
                -X GET

    **Response Example:**

    .. code-block:: json

    {
        "average_rating": 5.0,
        "latest_reviews": [
            {
                "created": "Thu, 01 Sep 2022 14:06:33 GMT",
                "edits": 0,
                "entity_id": "233d58f7-aba4-405a-8cd3-4adb344bd333",
                "entity_type": "work",
                "full_name": "Creative Commons Attribution-ShareAlike 3.0 Unported",
                "id": "f8278997-bfd5-4d0e-8b9a-afb575bb1080",
                "info_url": "https://creativecommons.org/licenses/by-sa/3.0/",
                "is_draft": false,
                "is_hidden": false,
                "language": "en",
                "last_revision": {
                    "id": 11784,
                    "rating": 5,
                    "review_id": "f8278997-bfd5-4d0e-8b9a-afb575bb1080",
                    "text": null,
                    "timestamp": "Thu, 01 Sep 2022 14:06:33 GMT"
                },
                "last_updated": "Thu, 01 Sep 2022 14:06:33 GMT",
                "license_id": "CC BY-SA 3.0",
                "popularity": 0,
                "published_on": "Thu, 01 Sep 2022 14:06:33 GMT",
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
                "created": "Thu, 01 Sep 2022 14:06:33 GMT",
                "edits": 0,
                "entity_id": "233d58f7-aba4-405a-8cd3-4adb344bd333",
                "entity_type": "work",
                "full_name": "Creative Commons Attribution-ShareAlike 3.0 Unported",
                "id": "f8278997-bfd5-4d0e-8b9a-afb575bb1080",
                "info_url": "https://creativecommons.org/licenses/by-sa/3.0/",
                "is_draft": false,
                "is_hidden": false,
                "language": "en",
                "last_revision": {
                    "id": 11784,
                    "rating": 5,
                    "review_id": "f8278997-bfd5-4d0e-8b9a-afb575bb1080",
                    "text": null,
                    "timestamp": "Thu, 01 Sep 2022 14:06:33 GMT"
                },
                "last_updated": "Thu, 01 Sep 2022 14:06:33 GMT",
                "license_id": "CC BY-SA 3.0",
                "popularity": 0,
                "published_on": "Thu, 01 Sep 2022 14:06:33 GMT",
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
        "work": {
            "artist-rels": [
                {
                    "artist": {
                        "life-span": {
                            "begin": "1998"
                        },
                        "mbid": "663f33f4-8e5f-4773-93ea-493a1135de9a",
                        "name": "Tones and I",
                        "sort_name": "Tones and I",
                        "type": "Person"
                    },
                    "begin-year": null,
                    "direction": "backward",
                    "end-year": null,
                    "type": "composer",
                    "type-id": "d59d99ea-23d4-4a80-b066-edca32ee158f"
                },
                {
                    "artist": {
                        "life-span": {
                            "begin": "1998"
                        },
                        "mbid": "663f33f4-8e5f-4773-93ea-493a1135de9a",
                        "name": "Tones and I",
                        "sort_name": "Tones and I",
                        "type": "Person"
                    },
                    "begin-year": null,
                    "direction": "backward",
                    "end-year": null,
                    "type": "lyricist",
                    "type-id": "3e48faba-ec01-47fd-8e89-30e81161661c"
                }
            ],
            "mbid": "233d58f7-aba4-405a-8cd3-4adb344bd333",
            "name": "Dance Monkey",
            "recording-rels": [
                {
                    "begin-year": null,
                    "direction": "backward",
                    "end-year": null,
                    "recording": {
                        "length": 208.823,
                        "mbid": "a24895fe-c0a1-41eb-b695-3dbddbe2cb36",
                        "name": "Dance Monkey"
                    },
                    "type": "performance",
                    "type-id": "a3005666-a872-32c3-ad06-98af558e99b0"
                },
                {
                    "begin-year": null,
                    "direction": "backward",
                    "end-year": null,
                    "recording": {
                        "comment": "Nath Jennings bootleg",
                        "mbid": "fceef8ab-f844-45e8-822a-12d0ed536a4c",
                        "name": "Dance Monkey"
                    },
                    "type": "performance",
                    "type-id": "a3005666-a872-32c3-ad06-98af558e99b0"
                },
                {
                    "begin-year": null,
                    "direction": "backward",
                    "end-year": null,
                    "recording": {
                        "length": 234.0,
                        "mbid": "0ae5d3b3-2756-40b0-98cd-4a913351a42f",
                        "name": "Dance Monkey"
                    },
                    "type": "performance",
                    "type-id": "a3005666-a872-32c3-ad06-98af558e99b0"
                },
                {
                    "begin-year": null,
                    "direction": "backward",
                    "end-year": null,
                    "recording": {
                        "length": 177.449,
                        "mbid": "c73f942a-1c06-4034-86a2-d9f2090ada18",
                        "name": "Dance Monkey"
                    },
                    "type": "performance",
                    "type-id": "a3005666-a872-32c3-ad06-98af558e99b0"
                }
            ],
            "type": "Song"
        }
    }

    :statuscode 200: no error
    :statuscode 404: work not found

    :query username: User's username **(optional)**

    :resheader Content-Type: *application/json*
    """

    work = db_work.get_work_by_mbid(str(work_mbid))

    if not work:
        raise NotFound("Can't find a work with ID: {work_mbid}".format(work_mbid=work_mbid))

    user_review = None

    username = Parser.string('uri', 'username', optional=True)
    if username:
        user_review_cache_key = cache.gen_key('entity_api', work['mbid'], username, "user_review")
        user_review = cache.get(user_review_cache_key)
        if not user_review:
            user = db_users.get_by_mbid(username)
            if user:
                user_id = user['id']

                user_review, _ = db_review.list_reviews(
                    entity_id=work['mbid'],
                    entity_type='work',
                    user_id=user_id
                )
                if user_review:
                    user_review = db_review.to_dict(user_review[0])

                cache.set(user_review_cache_key, user_review,
                          expirein=REVIEW_CACHE_TIMEOUT, namespace=REVIEW_CACHE_NAMESPACE)

            else:
                user_review = []

    ratings_stats, average_rating = db_rating_stats.get_stats(work_mbid, "work")

    top_reviews_cache_key = cache.gen_key("entity_api_work", work['mbid'], "top_reviews")
    top_reviews_cached_result = cache.get(top_reviews_cache_key, REVIEW_CACHE_NAMESPACE)

    if top_reviews_cached_result:
        top_reviews, reviews_count = top_reviews_cached_result
    else:
        top_reviews, reviews_count = db_review.list_reviews(
            entity_id=work['mbid'],
            entity_type='work',
            sort='popularity',
            limit=REVIEWS_LIMIT,
            offset=0,
        )
        top_reviews = [db_review.to_dict(review) for review in top_reviews]

        cache.set(top_reviews_cache_key, (top_reviews, reviews_count),
                  expirein=REVIEW_CACHE_TIMEOUT, namespace=REVIEW_CACHE_NAMESPACE)

    latest_reviews_cache_key = cache.gen_key("entity_api_work", work['mbid'], "latest_reviews")
    latest_reviews_cached_result = cache.get(latest_reviews_cache_key, REVIEW_CACHE_NAMESPACE)

    if latest_reviews_cached_result:
        latest_reviews, reviews_count = latest_reviews_cached_result
    else:
        latest_reviews, reviews_count = db_review.list_reviews(
            entity_id=work['mbid'],
            entity_type='work',
            sort='published_on',
            limit=REVIEWS_LIMIT,
            offset=0,
        )
        latest_reviews = [db_review.to_dict(review) for review in latest_reviews]

        cache.set(latest_reviews_cache_key, (latest_reviews, reviews_count),
                  expirein=REVIEW_CACHE_TIMEOUT, namespace=REVIEW_CACHE_NAMESPACE)

    result = {
        "work": work,
        "average_rating": average_rating,
        "ratings_stats": ratings_stats,
        "reviews_count": reviews_count,
        "top_reviews": top_reviews,
        "latest_reviews": latest_reviews
    }

    if username:
        result['user_review'] = user_review

    return jsonify(**result)
