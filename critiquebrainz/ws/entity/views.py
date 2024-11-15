from flask import Blueprint, jsonify
import critiquebrainz.db.review as db_review
import critiquebrainz.db.users as db_users
import critiquebrainz.db.rating_stats as db_rating_stats
from critiquebrainz.frontend.external.entities import get_entity_by_id
from critiquebrainz.decorators import crossdomain
from critiquebrainz.ws.exceptions import NotFound
from critiquebrainz.ws.parser import Parser
from critiquebrainz.ws import REVIEWS_LIMIT, REVIEW_CACHE_NAMESPACE, REVIEW_CACHE_TIMEOUT
from brainzutils import cache
from werkzeug.routing import BaseConverter

entity_bp = Blueprint('ws_entity', __name__)

ENTITY_URL_TYPE_MAPPING = {
    "release-group": "release_group",
    "artist": "artist",
    "label": "label",
    "place": "place",
    "event": "event",
    "work": "work",
    "recording": "recording",
    "series": "bb_series",
    "edition-proup": "bb_edition_group",
    "literary-work": "bb_literary_work",
    "author": "bb_author",
}

class EntityNameConverter(BaseConverter):
    """This converter only accepts valid entity names from ENTITY_URL_TYPE_MAPPING
    
    Rule('/<entity_name:entity_name>')
    """

    def __init__(self, url_map):
        super().__init__(url_map)
        # Create regex pattern from valid entity names
        entity_names = '|'.join(ENTITY_URL_TYPE_MAPPING.keys())
        self.regex = f"({entity_names})"

    def to_python(self, value):
        return value

    def to_url(self, value):
        return str(value)


def _get_cached_reviews(entity_id: str, entity_type: str, sort_type: str, 
                       cache_namespace: str = REVIEW_CACHE_NAMESPACE) -> tuple[list, int]:
    """Helper function to fetch and cache reviews."""
    cache_key = cache.gen_key(f"entity_api_{entity_type}", entity_id, f"{sort_type}_reviews")
    cached_result = cache.get(cache_key, cache_namespace)

    if cached_result:
        return cached_result

    reviews, count = db_review.list_reviews(
        entity_id=entity_id,
        entity_type=entity_type,
        sort=sort_type,
        limit=REVIEWS_LIMIT,
        offset=0,
    )
    reviews = [db_review.to_dict(review) for review in reviews]

    cache.set(cache_key, (reviews, count),
              expirein=REVIEW_CACHE_TIMEOUT, namespace=cache_namespace)
    return reviews, count


@entity_bp.route('/<entity_name:entity_name>/<uuid:entity_id>', methods=['GET', 'OPTIONS'])
@crossdomain(headers="Authorization, Content-Type")
def entity_handler(entity_name: str, entity_id: str):
    """Get list of reviews.

    **Request Example:**

    .. code-block:: bash

        $ curl "https://critiquebrainz.org/ws/1/<entity>/e6f48cbd-26de-4c2e-a24a-29892f9eb3be" \\
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
        "entity": {
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

    entity_type = ENTITY_URL_TYPE_MAPPING.get(entity_name)
    entity = get_entity_by_id(entity_id, entity_type)
    if not entity:
        raise NotFound(f"Can't find a {entity_name} with ID: {entity_id}")

    # Get user review if username provided
    user_review = []
    username = Parser.string('uri', 'username', optional=True)
    if username:
        cache_key = cache.gen_key('entity_api', entity_id, entity_type, username, "user_review")
        user_review = cache.get(cache_key, REVIEW_CACHE_NAMESPACE)

        if not user_review:
            user = db_users.get_by_mbid(username)
            if user:
                reviews, _ = db_review.list_reviews(
                    entity_id=entity_id,
                    entity_type=entity_type,
                    user_id=user['id']
                )
                user_review = db_review.to_dict(reviews[0]) if reviews else []
                cache.set(cache_key, user_review,
                         expirein=REVIEW_CACHE_TIMEOUT, namespace=REVIEW_CACHE_NAMESPACE)

    # Get ratings and reviews
    ratings_stats, average_rating = db_rating_stats.get_stats(entity_id, entity_type)
    top_reviews, reviews_count = _get_cached_reviews(entity_id, entity_type, 'popularity')
    latest_reviews, _ = _get_cached_reviews(entity_id, entity_type, 'published_on')

    result = {
        "entity": entity,
        "average_rating": average_rating,
        "ratings_stats": ratings_stats,
        "reviews_count": reviews_count,
        "top_reviews": top_reviews,
        "latest_reviews": latest_reviews
    }

    if username:
        result['user_review'] = user_review

    return jsonify(result)
