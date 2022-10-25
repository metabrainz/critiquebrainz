from flask import Blueprint, jsonify
import critiquebrainz.db.review as db_review
import critiquebrainz.db.users as db_users
import critiquebrainz.db.rating_stats as db_rating_stats
from critiquebrainz.frontend.external.musicbrainz_db import place as db_place
from critiquebrainz.decorators import crossdomain
from critiquebrainz.ws.exceptions import NotFound
from critiquebrainz.ws.parser import Parser
from critiquebrainz.ws import REVIEWS_LIMIT, REVIEW_CACHE_NAMESPACE, REVIEW_CACHE_TIMEOUT
from brainzutils import cache

place_bp = Blueprint('ws_place', __name__)


@place_bp.route('/<uuid:place_mbid>', methods=['GET', 'OPTIONS'])
@crossdomain(headers="Authorization, Content-Type")
def place_entity_handler(place_mbid):
    """Get list of reviews.

    **Request Example:**

    .. code-block:: bash

        $ curl "https://critiquebrainz.org/ws/1/place/8da8cd3d-6162-4714-ad96-6d7c276f4f8a" \\
                -X GET

    **Response Example:**

    .. code-block:: json

    {
        "average_rating": 0,
        "latest_reviews": [
            {
                "created": "Sun, 13 Mar 2016 12:16:52 GMT",
                "edits": 0,
                "entity_id": "8da8cd3d-6162-4714-ad96-6d7c276f4f8a",
                "entity_type": "place",
                "full_name": "Creative Commons Attribution-ShareAlike 3.0 Unported",
                "id": "dd4b5498-ee04-4663-80f1-22eb5601c68b",
                "info_url": "https://creativecommons.org/licenses/by-sa/3.0/",
                "is_draft": false,
                "is_hidden": false,
                "language": "en",
                "last_revision": {
                    "id": 9796,
                    "rating": null,
                    "review_id": "dd4b5498-ee04-4663-80f1-22eb5601c68b",
                    "text": "The Elbphilharmonie was hyped a lot but so far has failed lived up to everyone's expectations.\r\nThe delay of seven years only proves that large prestige projects in Germany do not tend to go well while costs skyrocket.\r\n\r\nI am though intrigued by the acoustics of the main concert hall, which will hopefully be as good as advertised.",
                    "timestamp": "Sun, 13 Mar 2016 12:17:09 GMT"
                },
                "last_updated": "Sun, 13 Mar 2016 12:17:09 GMT",
                "license_id": "CC BY-SA 3.0",
                "popularity": -3,
                "published_on": "Sun, 13 Mar 2016 12:17:09 GMT",
                "rating": null,
                "source": null,
                "source_url": null,
                "text": "The Elbphilharmonie was hyped a lot but so far has failed lived up to everyone's expectations.\r\nThe delay of seven years only proves that large prestige projects in Germany do not tend to go well while costs skyrocket.\r\n\r\nI am though intrigued by the acoustics of the main concert hall, which will hopefully be as good as advertised.",
                "user": {
                    "created": "Thu, 19 Feb 2015 15:05:21 GMT",
                    "display_name": "Leo Verto",
                    "id": "f0aeeddc-0682-42bb-a340-b5773ca6f2c8",
                    "karma": -3,
                    "user_type": "Noob"
                },
                "votes_negative_count": 3,
                "votes_positive_count": 0
            }
        ],
        "place": {
            "address": "Am Kaiserkai 1, 20457 Hamburg",
            "area": {
                "mbid": "11a44e18-a2e5-43a9-bee9-aa4f7c83f967",
                "name": "Hamburg"
            },
            "artist-rels": [
                {
                    "artist": {
                        "life-span": {
                            "begin": "1976-11-30"
                        },
                        "mbid": "7d98417c-60b0-4567-b807-a250c25261ef",
                        "name": "Iveta Apkalna",
                        "sort_name": "Apkalna, Iveta",
                        "type": "Person"
                    },
                    "begin-year": 2017,
                    "direction": "backward",
                    "end-year": null,
                    "type": "organist",
                    "type-id": "cad0dbab-c711-442a-a91c-05359f0228ce"
                },
                {
                    "artist": {
                        "comment": "1945\u20132016: NDR Sinfonieorchester",
                        "life-span": {
                            "begin": "1945"
                        },
                        "mbid": "2688f91d-dfdd-4d67-94df-0f1a02140c62",
                        "name": "NDR Elbphilharmonie Orchester",
                        "sort_name": "NDR Elbphilharmonie Orchester",
                        "type": "Orchestra"
                    },
                    "begin-year": 2017,
                    "direction": "backward",
                    "end-year": null,
                    "type": "primary concert venue",
                    "type-id": "fff4640a-0819-49e9-92c5-1e3b5134fd95"
                }
            ],
            "comment": "concert hall in Hamburg",
            "coordinates": {
                "latitude": 53.541238,
                "longitude": 9.984255
            },
            "external-urls": [
                {
                    "begin-year": null,
                    "direction": "forward",
                    "end-year": null,
                    "icon": "discogs-16.png",
                    "name": "Discogs",
                    "type": "discogs",
                    "type-id": "1c140ac8-8dc2-449e-92cb-52c90d525640",
                    "url": {
                        "mbid": "96b51b85-0780-488a-bc71-902fb473595d",
                        "url": "https://www.discogs.com/label/1153802"
                    }
                },
                {
                    "begin-year": null,
                    "direction": "forward",
                    "end-year": null,
                    "icon": "home-16.png",
                    "name": "Official homepage",
                    "type": "official homepage",
                    "type-id": "696b79da-7e45-40e6-a9d4-b31438eb7e5d",
                    "url": {
                        "mbid": "551b47c5-0b3b-49d2-aa5a-e3a5fc76c0c9",
                        "url": "http://www.elbphilharmonie.de/"
                    }
                },
                {
                    "begin-year": null,
                    "direction": "forward",
                    "end-year": null,
                    "icon": "wikidata-16.png",
                    "name": "Wikidata",
                    "type": "wikidata",
                    "type-id": "e6826618-b410-4b8d-b3b5-52e29eac5e1f",
                    "url": {
                        "mbid": "7add6c0d-c644-4565-bb4e-09ad6f147568",
                        "url": "https://www.wikidata.org/wiki/Q673223"
                    }
                }
            ],
            "life-span": {
                "begin": "2017-01-11"
            },
            "mbid": "8da8cd3d-6162-4714-ad96-6d7c276f4f8a",
            "name": "Elbphilharmonie",
            "parts": [
                {
                    "begin-year": null,
                    "direction": "forward",
                    "end-year": null,
                    "place": {
                        "address": "Am Kaiserkai 1, 20457 Hamburg",
                        "area": {
                            "mbid": "11a44e18-a2e5-43a9-bee9-aa4f7c83f967",
                            "name": "Hamburg"
                        },
                        "coordinates": {
                            "latitude": 53.541238,
                            "longitude": 9.984255
                        },
                        "mbid": "b3aa8167-f92f-48d6-a3bf-e20c8e20c6b5",
                        "name": "Elbphilharmonie: Kaistudio 1"
                    },
                    "type": "parts",
                    "type-id": "ff683f48-eff1-40ab-a58f-b128098ffe92"
                },
                {
                    "begin-year": null,
                    "direction": "forward",
                    "end-year": null,
                    "place": {
                        "address": "Platz der Deutschen Einheit 1, 20457 Hamburg",
                        "area": {
                            "mbid": "11a44e18-a2e5-43a9-bee9-aa4f7c83f967",
                            "name": "Hamburg"
                        },
                        "coordinates": {
                            "latitude": 53.54133,
                            "longitude": 9.98447
                        },
                        "mbid": "9fc8d3da-e7f1-404c-a615-e9794d57ddb6",
                        "name": "Elbphilharmonie: Gro\u00dfer Saal",
                        "type": "Venue"
                    },
                    "type": "parts",
                    "type-id": "ff683f48-eff1-40ab-a58f-b128098ffe92"
                },
                {
                    "begin-year": null,
                    "direction": "forward",
                    "end-year": null,
                    "place": {
                        "address": "",
                        "area": {
                            "mbid": "11a44e18-a2e5-43a9-bee9-aa4f7c83f967",
                            "name": "Hamburg"
                        },
                        "mbid": "e810f624-7423-4efa-9cb4-de2e081cc755",
                        "name": "Elbphilharmonie: Kleiner Saal",
                        "type": "Venue"
                    },
                    "type": "parts",
                    "type-id": "ff683f48-eff1-40ab-a58f-b128098ffe92"
                }
            ],
            "type": "Venue",
            "url-rels": [
                {
                    "begin-year": null,
                    "direction": "forward",
                    "end-year": null,
                    "type": "official homepage",
                    "type-id": "696b79da-7e45-40e6-a9d4-b31438eb7e5d",
                    "url": {
                        "mbid": "551b47c5-0b3b-49d2-aa5a-e3a5fc76c0c9",
                        "url": "http://www.elbphilharmonie.de/"
                    }
                },
                {
                    "begin-year": null,
                    "direction": "forward",
                    "end-year": null,
                    "type": "discogs",
                    "type-id": "1c140ac8-8dc2-449e-92cb-52c90d525640",
                    "url": {
                        "mbid": "96b51b85-0780-488a-bc71-902fb473595d",
                        "url": "https://www.discogs.com/label/1153802"
                    }
                },
                {
                    "begin-year": null,
                    "direction": "forward",
                    "end-year": null,
                    "type": "songkick",
                    "type-id": "3eb58d3e-6f00-36a8-a115-3dad616b7391",
                    "url": {
                        "mbid": "97b4b49f-aa9c-4809-ae63-6184896655df",
                        "url": "https://www.songkick.com/venues/914796"
                    }
                },
                {
                    "begin-year": null,
                    "direction": "forward",
                    "end-year": null,
                    "type": "image",
                    "type-id": "68a4537c-f2a6-49b8-81c5-82a62b0976b7",
                    "url": {
                        "mbid": "cfdaf6e4-7e68-4aa1-9053-211afaf4bbd3",
                        "url": "https://commons.wikimedia.org/wiki/File:Elbphilharmonie,_Hamburg.jpg"
                    }
                }
            ]
        },
        "ratings_stats": {
            "1": 0,
            "2": 0,
            "3": 0,
            "4": 0,
            "5": 0
        },
        "reviews_count": 1,
        "top_reviews": [
            {
                "created": "Sun, 13 Mar 2016 12:16:52 GMT",
                "edits": 0,
                "entity_id": "8da8cd3d-6162-4714-ad96-6d7c276f4f8a",
                "entity_type": "place",
                "full_name": "Creative Commons Attribution-ShareAlike 3.0 Unported",
                "id": "dd4b5498-ee04-4663-80f1-22eb5601c68b",
                "info_url": "https://creativecommons.org/licenses/by-sa/3.0/",
                "is_draft": false,
                "is_hidden": false,
                "language": "en",
                "last_revision": {
                    "id": 9796,
                    "rating": null,
                    "review_id": "dd4b5498-ee04-4663-80f1-22eb5601c68b",
                    "text": "The Elbphilharmonie was hyped a lot but so far has failed lived up to everyone's expectations.\r\nThe delay of seven years only proves that large prestige projects in Germany do not tend to go well while costs skyrocket.\r\n\r\nI am though intrigued by the acoustics of the main concert hall, which will hopefully be as good as advertised.",
                    "timestamp": "Sun, 13 Mar 2016 12:17:09 GMT"
                },
                "last_updated": "Sun, 13 Mar 2016 12:17:09 GMT",
                "license_id": "CC BY-SA 3.0",
                "popularity": -3,
                "published_on": "Sun, 13 Mar 2016 12:17:09 GMT",
                "rating": null,
                "source": null,
                "source_url": null,
                "text": "The Elbphilharmonie was hyped a lot but so far has failed lived up to everyone's expectations.\r\nThe delay of seven years only proves that large prestige projects in Germany do not tend to go well while costs skyrocket.\r\n\r\nI am though intrigued by the acoustics of the main concert hall, which will hopefully be as good as advertised.",
                "user": {
                    "created": "Thu, 19 Feb 2015 15:05:21 GMT",
                    "display_name": "Leo Verto",
                    "id": "f0aeeddc-0682-42bb-a340-b5773ca6f2c8",
                    "karma": -3,
                    "user_type": "Noob"
                },
                "votes_negative_count": 3,
                "votes_positive_count": 0
            }
        ]
    }

    :statuscode 200: no error
    :statuscode 404: place not found

    :query username: User's username **(optional)**

    :resheader Content-Type: *application/json*
    """

    place = db_place.get_place_by_mbid(str(place_mbid))

    if not place:
        raise NotFound("Can't find a place with ID: {place_mbid}".format(place_mbid=place_mbid))

    user_review = None

    username = Parser.string('uri', 'username', optional=True)
    if username:
        user_review_cache_key = cache.gen_key('entity_api', place['mbid'], username, "user_review")
        user_review = cache.get(user_review_cache_key, REVIEW_CACHE_NAMESPACE)
        if not user_review:
            user = db_users.get_by_mbid(username)
            if user:
                user_id = user['id']

                user_review, _ = db_review.list_reviews(
                    entity_id=place['mbid'],
                    entity_type='place',
                    user_id=user_id
                )
                if user_review:
                    user_review = db_review.to_dict(user_review[0])

                cache.set(user_review_cache_key, user_review,
                        expirein=REVIEW_CACHE_TIMEOUT, namespace=REVIEW_CACHE_NAMESPACE)

            else:
                user_review = []

    ratings_stats, average_rating = db_rating_stats.get_stats(place_mbid, "place")

    top_reviews_cache_key = cache.gen_key("entity_api_place", place['mbid'], "top_reviews")
    top_reviews_cached_result = cache.get(top_reviews_cache_key, REVIEW_CACHE_NAMESPACE)

    if top_reviews_cached_result:
        top_reviews, reviews_count = top_reviews_cached_result
    else:
        top_reviews, reviews_count = db_review.list_reviews(
            entity_id=place['mbid'],
            entity_type='place',
            sort='popularity',
            limit=REVIEWS_LIMIT,
            offset=0,
        )
        top_reviews = [db_review.to_dict(review) for review in top_reviews]

        cache.set(top_reviews_cache_key, (top_reviews, reviews_count),
                  expirein=REVIEW_CACHE_TIMEOUT, namespace=REVIEW_CACHE_NAMESPACE)

    latest_reviews_cache_key = cache.gen_key("entity_api_place", place['mbid'], "latest_reviews")
    latest_reviews_cached_result = cache.get(latest_reviews_cache_key, REVIEW_CACHE_NAMESPACE)

    if latest_reviews_cached_result:
        latest_reviews, reviews_count = latest_reviews_cached_result
    else:
        latest_reviews, reviews_count = db_review.list_reviews(
            entity_id=place['mbid'],
            entity_type='place',
            sort='published_on',
            limit=REVIEWS_LIMIT,
            offset=0,
        )
        latest_reviews = [db_review.to_dict(review) for review in latest_reviews]

        cache.set(latest_reviews_cache_key, (latest_reviews, reviews_count),
                  expirein=REVIEW_CACHE_TIMEOUT, namespace=REVIEW_CACHE_NAMESPACE)

    result = {
        "place": place,
        "average_rating": average_rating,
        "ratings_stats": ratings_stats,
        "reviews_count": reviews_count,
        "top_reviews": top_reviews,
        "latest_reviews": latest_reviews
    }

    if username:
        result['user_review'] = user_review

    return jsonify(**result)
