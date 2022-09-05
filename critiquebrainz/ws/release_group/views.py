from flask import Blueprint, jsonify
import critiquebrainz.db.review as db_review
import critiquebrainz.db.rating_stats as db_rating_stats
from critiquebrainz.frontend.external.musicbrainz_db import release_group as db_release_group
from critiquebrainz.decorators import crossdomain
from critiquebrainz.ws.exceptions import NotFound
from critiquebrainz.ws.parser import Parser
from critiquebrainz.ws import REVIEWS_LIMIT, REVIEW_CACHE_NAMESPACE, REVIEW_CACHE_TIMEOUT
from brainzutils import cache


release_group_bp = Blueprint('ws_release_group', __name__)


@release_group_bp.route('/<uuid:release_group_mbid>', methods=['GET', 'OPTIONS'])
@crossdomain(headers="Authorization, Content-Type")
def release_group_entity_handler(release_group_mbid):
    """Get list of reviews.

    **Request Example:**

    .. code-block:: bash

        $ curl "https://critiquebrainz.org/ws/1/release-group/f0bd8ae8-321f-43d8-af87-e2f90d1b3817" \\
                -X GET

    **Response Example:**

    .. code-block:: json

    {
        "average_rating": 4.0,
        "latest_reviews": [
            {
                "created": "Wed, 01 Dec 2021 16:28:50 GMT",
                "edits": 0,
                "entity_id": "f0bd8ae8-321f-43d8-af87-e2f90d1b3817",
                "entity_type": "release_group",
                "full_name": "Creative Commons Attribution-ShareAlike 3.0 Unported",
                "id": "b08b37f6-c644-470d-af48-e77b14331e09",
                "info_url": "https://creativecommons.org/licenses/by-sa/3.0/",
                "is_draft": false,
                "is_hidden": false,
                "language": "en",
                "last_revision": {
                    "id": 11167,
                    "rating": 4,
                    "review_id": "b08b37f6-c644-470d-af48-e77b14331e09",
                    "text": "Hollywood Greats, a cover mount from The Daily Mirror, was one of my first ever newspaper cover mounts I got - and sadly it led me to believe that all newspaper covermounts were free goldmines ready to be plundered; how wrong was I!\r\n\r\n10 great original studio recordings, and 5 so-so tracks from \"underground\" artists, however those 5 artists were so underground that even the internet knows nothing of them.\r\n\r\nI'm probably biased with this one as it was my first - but a good collection either way.",
                    "timestamp": "Wed, 01 Dec 2021 16:28:50 GMT"
                },
                "last_updated": "Wed, 01 Dec 2021 16:28:50 GMT",
                "license_id": "CC BY-SA 3.0",
                "popularity": 1,
                "published_on": "Wed, 01 Dec 2021 16:28:50 GMT",
                "rating": 4,
                "source": null,
                "source_url": null,
                "text": "Hollywood Greats, a cover mount from The Daily Mirror, was one of my first ever newspaper cover mounts I got - and sadly it led me to believe that all newspaper covermounts were free goldmines ready to be plundered; how wrong was I!\r\n\r\n10 great original studio recordings, and 5 so-so tracks from \"underground\" artists, however those 5 artists were so underground that even the internet knows nothing of them.\r\n\r\nI'm probably biased with this one as it was my first - but a good collection either way.",
                "user": {
                    "created": "Sat, 15 Aug 2020 15:48:39 GMT",
                    "display_name": "sound.and.vision",
                    "id": "dfdae69f-275f-41a2-82c7-ac5d1f9c8129",
                    "karma": 27,
                    "user_type": "Noob"
                },
                "votes_negative_count": 0,
                "votes_positive_count": 1
            }
        ],
        "ratings_stats": {
            "1": 0,
            "2": 0,
            "3": 0,
            "4": 1,
            "5": 0
        },
        "release_group": {
            "artist-credit": [
                {
                    "artist": {
                        "comment": "add compilations to this artist",
                        "mbid": "89ad4ac3-39f7-470e-963a-56509c546377",
                        "name": "Various Artists",
                        "sort_name": "Various Artists",
                        "type": "Other"
                    },
                    "name": "Various Artists"
                }
            ],
            "artist-credit-phrase": "Various Artists",
            "first-release-year": 2004,
            "mbid": "f0bd8ae8-321f-43d8-af87-e2f90d1b3817",
            "rating": 60,
            "release-list": [
                {
                    "mbid": "f51d400c-3303-447f-8f3c-595e1b1352bf",
                    "name": "Hollywood Greats"
                }
            ],
            "title": "Hollywood Greats",
            "type": "Album"
        },
        "reviews_count": 1,
        "top_reviews": [
            {
                "created": "Wed, 01 Dec 2021 16:28:50 GMT",
                "edits": 0,
                "entity_id": "f0bd8ae8-321f-43d8-af87-e2f90d1b3817",
                "entity_type": "release_group",
                "full_name": "Creative Commons Attribution-ShareAlike 3.0 Unported",
                "id": "b08b37f6-c644-470d-af48-e77b14331e09",
                "info_url": "https://creativecommons.org/licenses/by-sa/3.0/",
                "is_draft": false,
                "is_hidden": false,
                "language": "en",
                "last_revision": {
                    "id": 11167,
                    "rating": 4,
                    "review_id": "b08b37f6-c644-470d-af48-e77b14331e09",
                    "text": "Hollywood Greats, a cover mount from The Daily Mirror, was one of my first ever newspaper cover mounts I got - and sadly it led me to believe that all newspaper covermounts were free goldmines ready to be plundered; how wrong was I!\r\n\r\n10 great original studio recordings, and 5 so-so tracks from \"underground\" artists, however those 5 artists were so underground that even the internet knows nothing of them.\r\n\r\nI'm probably biased with this one as it was my first - but a good collection either way.",
                    "timestamp": "Wed, 01 Dec 2021 16:28:50 GMT"
                },
                "last_updated": "Wed, 01 Dec 2021 16:28:50 GMT",
                "license_id": "CC BY-SA 3.0",
                "popularity": 1,
                "published_on": "Wed, 01 Dec 2021 16:28:50 GMT",
                "rating": 4,
                "source": null,
                "source_url": null,
                "text": "Hollywood Greats, a cover mount from The Daily Mirror, was one of my first ever newspaper cover mounts I got - and sadly it led me to believe that all newspaper covermounts were free goldmines ready to be plundered; how wrong was I!\r\n\r\n10 great original studio recordings, and 5 so-so tracks from \"underground\" artists, however those 5 artists were so underground that even the internet knows nothing of them.\r\n\r\nI'm probably biased with this one as it was my first - but a good collection either way.",
                "user": {
                    "created": "Sat, 15 Aug 2020 15:48:39 GMT",
                    "display_name": "sound.and.vision",
                    "id": "dfdae69f-275f-41a2-82c7-ac5d1f9c8129",
                    "karma": 27,
                    "user_type": "Noob"
                },
                "votes_negative_count": 0,
                "votes_positive_count": 1
            }
        ]
    }

    :statuscode 200: no error
    :statuscode 404: release group not found

    :resheader Content-Type: *application/json*
    """

    release_group = db_release_group.get_release_group_by_mbid(str(release_group_mbid))

    if not release_group:
        raise NotFound("Can't find a release group with ID: {release_group_mbid}".format(release_group_mbid=release_group_mbid))

    user_review = None

    user_id = Parser.uuid('uri', 'user_id', optional=True)
    if user_id:
        user_review_cache_key = cache.gen_key('entity_api', release_group['mbid'], user_id, "user_review")
        user_review = cache.get(user_review_cache_key)
        if not user_review:
            user_review, _ = db_review.list_reviews(
                entity_id=release_group['mbid'],
                entity_type='release_group',
                user_id=user_id
            )
            if user_review:
                user_review = db_review.to_dict(user_review[0])
            else:
                user_review = None

            cache.set(user_review_cache_key, user_review,
                      expirein=REVIEW_CACHE_TIMEOUT, namespace=REVIEW_CACHE_NAMESPACE)

    ratings_stats, average_rating = db_rating_stats.get_stats(release_group_mbid, "release_group")

    top_reviews_cache_key = cache.gen_key("entity_api_release_group", release_group['mbid'], "top_reviews")
    top_reviews_cached_result = cache.get(top_reviews_cache_key, REVIEW_CACHE_NAMESPACE)

    if top_reviews_cached_result:
        top_reviews, reviews_count = top_reviews_cached_result
    else:
        top_reviews, reviews_count = db_review.list_reviews(
            entity_id=release_group['mbid'],
            entity_type='release_group',
            sort='popularity',
            limit=REVIEWS_LIMIT,
            offset=0,
        )
        top_reviews = [db_review.to_dict(review) for review in top_reviews]

        cache.set(top_reviews_cache_key, (top_reviews, reviews_count),
                  expirein=REVIEW_CACHE_TIMEOUT, namespace=REVIEW_CACHE_NAMESPACE)

    latest_reviews_cache_key = cache.gen_key("entity_api_release_group", release_group['mbid'], "latest_reviews")
    latest_reviews_cached_result = cache.get(latest_reviews_cache_key, REVIEW_CACHE_NAMESPACE)

    if latest_reviews_cached_result:
        latest_reviews, reviews_count = latest_reviews_cached_result
    else:
        latest_reviews, reviews_count = db_review.list_reviews(
            entity_id=release_group['mbid'],
            entity_type='release_group',
            sort='published_on',
            limit=REVIEWS_LIMIT,
            offset=0,
        )
        latest_reviews = [db_review.to_dict(review) for review in latest_reviews]

        cache.set(latest_reviews_cache_key, (latest_reviews, reviews_count),
                  expirein=REVIEW_CACHE_TIMEOUT, namespace=REVIEW_CACHE_NAMESPACE)

    result = {
        "release_group": release_group,
        "average_rating": average_rating,
        "ratings_stats": ratings_stats,
        "reviews_count": reviews_count,
        "top_reviews": top_reviews,
        "latest_reviews": latest_reviews
    }
    if user_id:
        result['user_review'] = user_review

    return jsonify(**result)
