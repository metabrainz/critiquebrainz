from flask import Blueprint, jsonify
import critiquebrainz.db.review as db_review
import critiquebrainz.db.rating_stats as db_rating_stats
from critiquebrainz.frontend.external.bookbrainz_db import edition_group as db_edition_group
from critiquebrainz.decorators import crossdomain
from critiquebrainz.ws.exceptions import NotFound
from critiquebrainz.ws.parser import Parser
from critiquebrainz.ws import REVIEWS_LIMIT

edition_group_bp = Blueprint('ws_edition_group', __name__)


@edition_group_bp.route('/<uuid:edition_group_bbid>', methods=['GET', 'OPTIONS'])
@crossdomain(headers="Authorization, Content-Type")
def edition_group_entity_handler(edition_group_bbid):
    """Get list of reviews.

    **Request Example:**

    .. code-block:: bash

        $ curl "https://critiquebrainz.org/ws/1/edition-group/b2a5f76e-91c6-46bb-a618-3ee5ebc6dd6c" \\
                -X GET

    **Response Example:**

    .. code-block:: json

    {
        "average_rating": 5.0,
        "edition_group": {
            "author_credits": [],
            "bbid": "b2a5f76e-91c6-46bb-a618-3ee5ebc6dd6c",
            "disambiguation": null,
            "edition_group_type": "Book",
            "identifier_set_id": 1272,
            "identifiers": [
                {
                    "icon": "wikidata-16.png",
                    "name": "Wikidata ID",
                    "url": "https://www.wikidata.org/wiki/Q47209",
                    "value": "Q47209"
                }
            ],
            "name": "Harry Potter and the Chamber of Secrets",
            "relationship_set_id": null,
            "rels": null,
            "sort_name": "Chamber of Secrets, Harry Potter and the"
        },
        "latest_reviews": [
            {
                "created": "Thu, 28 Jul 2022 07:03:41 GMT",
                "edits": 0,
                "entity_id": "b2a5f76e-91c6-46bb-a618-3ee5ebc6dd6c",
                "entity_type": "bb_edition_group",
                "full_name": "Creative Commons Attribution-ShareAlike 3.0 Unported",
                "id": "84b01e18-50ac-484e-9e48-41d05250db76",
                "info_url": "https://creativecommons.org/licenses/by-sa/3.0/",
                "is_draft": false,
                "is_hidden": false,
                "language": "en",
                "last_revision": {
                    "id": 11786,
                    "rating": 5,
                    "review_id": "84b01e18-50ac-484e-9e48-41d05250db76",
                    "text": null,
                    "timestamp": "Fri, 02 Sep 2022 09:58:44 GMT"
                },
                "last_updated": "Fri, 02 Sep 2022 09:58:44 GMT",
                "license_id": "CC BY-SA 3.0",
                "popularity": 0,
                "published_on": "Thu, 28 Jul 2022 07:03:41 GMT",
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
                "created": "Thu, 28 Jul 2022 07:03:41 GMT",
                "edits": 0,
                "entity_id": "b2a5f76e-91c6-46bb-a618-3ee5ebc6dd6c",
                "entity_type": "bb_edition_group",
                "full_name": "Creative Commons Attribution-ShareAlike 3.0 Unported",
                "id": "84b01e18-50ac-484e-9e48-41d05250db76",
                "info_url": "https://creativecommons.org/licenses/by-sa/3.0/",
                "is_draft": false,
                "is_hidden": false,
                "language": "en",
                "last_revision": {
                    "id": 11786,
                    "rating": 5,
                    "review_id": "84b01e18-50ac-484e-9e48-41d05250db76",
                    "text": null,
                    "timestamp": "Fri, 02 Sep 2022 09:58:44 GMT"
                },
                "last_updated": "Fri, 02 Sep 2022 09:58:44 GMT",
                "license_id": "CC BY-SA 3.0",
                "popularity": 0,
                "published_on": "Thu, 28 Jul 2022 07:03:41 GMT",
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
    :statuscode 404: edition group not found

    :resheader Content-Type: *application/json*
    """

    edition_group = db_edition_group.get_edition_group_by_bbid(str(edition_group_bbid))

    if not edition_group:
        raise NotFound("Can't find an edition_group with ID: {edition_group_bbid}".format(edition_group_bbid=edition_group_bbid))

    user_id = Parser.uuid('uri', 'user_id', optional=True)
    if user_id:
        user_review, _ = db_review.list_reviews(
            entity_id=edition_group['bbid'],
            entity_type='bb_edition_group',
            user_id=user_id
        )
        if user_review:
            user_review = db_review.to_dict(user_review[0])
        else:
            user_review = None

    ratings_stats, average_rating = db_rating_stats.get_stats(edition_group_bbid, "bb_edition_group")

    top_reviews, reviews_count = db_review.list_reviews(
        entity_id=edition_group['bbid'],
        entity_type='bb_edition_group',
        sort='popularity',
        limit=REVIEWS_LIMIT,
        offset=0,
    )

    latest_reviews, reviews_count = db_review.list_reviews(
        entity_id=edition_group['bbid'],
        entity_type='bb_edition_group',
        sort='published_on',
        limit=REVIEWS_LIMIT,
        offset=0,
    )

    top_reviews = [db_review.to_dict(review) for review in top_reviews]
    latest_reviews = [db_review.to_dict(review) for review in latest_reviews]

    result = {
        "edition_group": edition_group,
        "average_rating": average_rating,
        "ratings_stats": ratings_stats,
        "reviews_count": reviews_count,
        "top_reviews": top_reviews,
        "latest_reviews": latest_reviews
    }
    if user_id:
        result['user_review'] = user_review

    return jsonify(**result)
