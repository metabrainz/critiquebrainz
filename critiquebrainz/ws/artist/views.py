from flask import Blueprint, jsonify
import critiquebrainz.db.review as db_review
import critiquebrainz.db.rating_stats as db_rating_stats
from critiquebrainz.frontend.external.musicbrainz_db import artist as db_artist
from critiquebrainz.decorators import crossdomain
from critiquebrainz.ws.exceptions import NotFound
from critiquebrainz.ws.parser import Parser
from critiquebrainz.ws import REVIEWS_LIMIT, REVIEW_CACHE_NAMESPACE, REVIEW_CACHE_TIMEOUT
from brainzutils import cache

artist_bp = Blueprint('ws_artist', __name__)


@artist_bp.route('/<uuid:artist_mbid>', methods=['GET', 'OPTIONS'])
@crossdomain(headers="Authorization, Content-Type")
def artist_entity_handler(artist_mbid):
    """Get list of reviews.

    **Request Example:**

    .. code-block:: bash

        $ curl "https://critiquebrainz.org/ws/1/artist/df602ea4-c143-425d-a235-d7641f7634fd" \\
                -X GET

    **Response Example:**

    .. code-block:: json

        {
            "artist": {
                "artist-rels": [
                    {
                        "artist": {
                            "life-span": {
                                "begin": "1981-07-17"
                            },
                            "mbid": "60bc1e7d-d974-4205-bc9f-9dd3dba93534",
                            "name": "Sergey Semenov",
                            "sort_name": "Sergey Semenov",
                            "type": "Person"
                        },
                        "begin-year": 2011,
                        "direction": "backward",
                        "end-year": null,
                        "type": "member of band",
                        "type-id": "5be4c609-9afa-4ea0-910b-12ffb71e3821"
                    },
                    {
                        "artist": {
                            "life-span": {
                                "begin": "2020-10-01"
                            },
                            "mbid": "ba2f69b0-dcda-4f81-b324-17f73f36980c",
                            "name": "DJ Repeet",
                            "sort_name": "Repeet, DJ",
                            "type": "Character"
                        },
                        "begin-year": 2020,
                        "direction": "backward",
                        "end-year": null,
                        "type": "member of band",
                        "type-id": "5be4c609-9afa-4ea0-910b-12ffb71e3821"
                    }
                ],
                "band-members": [
                    {
                        "artist": {
                            "life-span": {
                                "begin": "1981-07-17"
                            },
                            "mbid": "60bc1e7d-d974-4205-bc9f-9dd3dba93534",
                            "name": "Sergey Semenov",
                            "sort_name": "Sergey Semenov",
                            "type": "Person"
                        },
                        "begin-year": 2011,
                        "direction": "backward",
                        "end-year": null,
                        "type": "member of band",
                        "type-id": "5be4c609-9afa-4ea0-910b-12ffb71e3821"
                    },
                    {
                        "artist": {
                            "life-span": {
                                "begin": "2020-10-01"
                            },
                            "mbid": "ba2f69b0-dcda-4f81-b324-17f73f36980c",
                            "name": "DJ Repeet",
                            "sort_name": "Repeet, DJ",
                            "type": "Character"
                        },
                        "begin-year": 2020,
                        "direction": "backward",
                        "end-year": null,
                        "type": "member of band",
                        "type-id": "5be4c609-9afa-4ea0-910b-12ffb71e3821"
                    }
                ],
                "external-urls": [
                    {
                        "begin-year": null,
                        "direction": "forward",
                        "end-year": null,
                        "icon": "discogs-16.png",
                        "name": "Discogs",
                        "type": "discogs",
                        "type-id": "04a5b104-a4c2-4bac-99a1-7b837c37d9e4",
                        "url": {
                            "mbid": "694f02d8-1be0-4c69-ae04-4c63686d3fdb",
                            "url": "https://www.discogs.com/artist/10091563"
                        }
                    }
                    {
                        "begin-year": null,
                        "direction": "forward",
                        "end-year": null,
                        "icon": "wikidata-16.png",
                        "name": "Wikidata",
                        "type": "wikidata",
                        "type-id": "689870a4-a1e4-4912-b17f-7b2664215698",
                        "url": {
                            "mbid": "bddc058d-4cb6-4ced-a05c-de3bf2b60692",
                            "url": "https://www.wikidata.org/wiki/Q109645393"
                        }
                    }
                ],
                "life-span": {
                    "begin": "2011-07-17"
                },
                "mbid": "df602ea4-c143-425d-a235-d7641f7634fd",
                "name": "Senkino",
                "sort_name": "Senkino",
                "type": "Group"
            },
            "average_rating": 5.0,
            "latest_reviews": [
                {
                    "created": "Wed, 24 Nov 2021 02:59:15 GMT",
                    "edits": 0,
                    "entity_id": "df602ea4-c143-425d-a235-d7641f7634fd",
                    "entity_type": "artist",
                    "full_name": "Creative Commons Attribution-ShareAlike 3.0 Unported",
                    "id": "0a3548a7-a014-4e71-a65b-d45fce677cf0",
                    "info_url": "https://creativecommons.org/licenses/by-sa/3.0/",
                    "is_draft": false,
                    "is_hidden": false,
                    "language": "en",
                    "last_revision": {
                        "id": 11139,
                        "rating": 5,
                        "review_id": "0a3548a7-a014-4e71-a65b-d45fce677cf0",
                        "text": null,
                        "timestamp": "Wed, 24 Nov 2021 02:59:15 GMT"
                    },
                    "last_updated": "Wed, 24 Nov 2021 02:59:15 GMT",
                    "license_id": "CC BY-SA 3.0",
                    "popularity": 0,
                    "published_on": "Wed, 24 Nov 2021 02:59:15 GMT",
                    "rating": 5,
                    "source": null,
                    "source_url": null,
                    "text": null,
                    "user": {
                        "created": "Wed, 24 Nov 2021 02:56:16 GMT",
                        "display_name": "Rada87",
                        "id": "5e784575-4bb8-4a9f-8334-2cb87f073cf0",
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
                    "created": "Wed, 24 Nov 2021 02:59:15 GMT",
                    "edits": 0,
                    "entity_id": "df602ea4-c143-425d-a235-d7641f7634fd",
                    "entity_type": "artist",
                    "full_name": "Creative Commons Attribution-ShareAlike 3.0 Unported",
                    "id": "0a3548a7-a014-4e71-a65b-d45fce677cf0",
                    "info_url": "https://creativecommons.org/licenses/by-sa/3.0/",
                    "is_draft": false,
                    "is_hidden": false,
                    "language": "en",
                    "last_revision": {
                        "id": 11139,
                        "rating": 5,
                        "review_id": "0a3548a7-a014-4e71-a65b-d45fce677cf0",
                        "text": null,
                        "timestamp": "Wed, 24 Nov 2021 02:59:15 GMT"
                    },
                    "last_updated": "Wed, 24 Nov 2021 02:59:15 GMT",
                    "license_id": "CC BY-SA 3.0",
                    "popularity": 0,
                    "published_on": "Wed, 24 Nov 2021 02:59:15 GMT",
                    "rating": 5,
                    "source": null,
                    "source_url": null,
                    "text": null,
                    "user": {
                        "created": "Wed, 24 Nov 2021 02:56:16 GMT",
                        "display_name": "Rada87",
                        "id": "5e784575-4bb8-4a9f-8334-2cb87f073cf0",
                        "karma": 0,
                        "user_type": "Noob"
                    },
                    "votes_negative_count": 0,
                    "votes_positive_count": 0
                }
            ]
        }

    :statuscode 200: no error
    :statuscode 404: artist not found

    :resheader Content-Type: *application/json*
    """

    artist = db_artist.get_artist_by_mbid(str(artist_mbid))
    if not artist:
        raise NotFound("Can't find an artist with ID: {artist_mbid}".format(artist_mbid=artist_mbid))

    user_review = None

    user_id = Parser.uuid('uri', 'user_id', optional=True)
    if user_id:
        user_review_cache_key = cache.gen_key('entity_api', artist['mbid'], user_id, "user_review")
        user_review = cache.get(user_review_cache_key)
        if not user_review:
            user_review, _ = db_review.list_reviews(
                entity_id=artist['mbid'],
                entity_type='artist',
                user_id=user_id
            )
            if user_review:
                user_review = db_review.to_dict(user_review[0])
            else:
                user_review = None

            cache.set(user_review_cache_key, user_review,
                      expirein=REVIEW_CACHE_TIMEOUT, namespace=REVIEW_CACHE_NAMESPACE)

    ratings_stats, average_rating = db_rating_stats.get_stats(artist_mbid, "artist")

    top_reviews_cache_key = cache.gen_key("entity_api_artist", artist['mbid'], "top_reviews")
    top_reviews_cached_result = cache.get(top_reviews_cache_key, REVIEW_CACHE_NAMESPACE)

    if top_reviews_cached_result:
        top_reviews, reviews_count = top_reviews_cached_result
    else:
        top_reviews, reviews_count = db_review.list_reviews(
            entity_id=artist['mbid'],
            entity_type='artist',
            sort='popularity',
            limit=REVIEWS_LIMIT,
            offset=0,
        )
        top_reviews = [db_review.to_dict(review) for review in top_reviews]

        cache.set(top_reviews_cache_key, (top_reviews, reviews_count),
                  expirein=REVIEW_CACHE_TIMEOUT, namespace=REVIEW_CACHE_NAMESPACE)

    latest_reviews_cache_key = cache.gen_key("entity_api_artist", artist['mbid'], "latest_reviews")
    latest_reviews_cached_result = cache.get(latest_reviews_cache_key, REVIEW_CACHE_NAMESPACE)

    if latest_reviews_cached_result:
        latest_reviews, reviews_count = latest_reviews_cached_result
    else:
        latest_reviews, reviews_count = db_review.list_reviews(
            entity_id=artist['mbid'],
            entity_type='artist',
            sort='published_on',
            limit=REVIEWS_LIMIT,
            offset=0,
        )
        latest_reviews = [db_review.to_dict(review) for review in latest_reviews]

        cache.set(latest_reviews_cache_key, (latest_reviews, reviews_count),
                  expirein=REVIEW_CACHE_TIMEOUT, namespace=REVIEW_CACHE_NAMESPACE)

    result = {
        "artist": artist,
        "average_rating": average_rating,
        "ratings_stats": ratings_stats,
        "reviews_count": reviews_count,
        "top_reviews": top_reviews,
        "latest_reviews": latest_reviews
    }
    if user_id:
        result['user_review'] = user_review

    return jsonify(**result)
