from flask import Blueprint, jsonify, request

from critiquebrainz.decorators import crossdomain
import critiquebrainz.db.review as db_review

bulk_review_bp = Blueprint('ws_review_bulk', __name__)


@bulk_review_bp.route('/', methods=['GET', 'OPTIONS'])
@crossdomain(headers="Authorization, Content-Type")
def bulk_review_entity_handler():
    """Get a list of reviews with specified UUIDs.

    .. note::

        Hidden reviews are omitted from the response. Invalid uuids and uuids not associated
        with a review are ignored.

    **Request Example:**

    .. code-block:: bash

       $ curl https://critiquebrainz.org/ws/1/reviews?review_ids=b7575c23-13d5-4adc-ac09-2f55a647d3de,e4364ed2-a5db-4427-8456-ea7604b499ef \\
              -X GET

    **Response Example:**

    .. code-block:: json

        {
          "reviews": {
            "b7575c23-13d5-4adc-ac09-2f55a647d3de": {
              "created": "Tue, 10 Aug 2010 00:00:00 GMT",
              "edits": 0,
              "entity_id": "03e0a99c-3530-4e64-8f50-6592325c2082",
              "entity_type": "release_group",
              "id": "b7575c23-13d5-4adc-ac09-2f55a647d3de",
              "language": "en",
              "last_updated": "Tue, 10 Aug 2010 00:00:00 GMT",
              "license": {
                "full_name": "Creative Commons Attribution-NonCommercial-ShareAlike 3.0 Unported",
                "id": "CC BY-NC-SA 3.0",
                "info_url": "https://creativecommons.org/licenses/by-nc-sa/3.0/"
              },
              "popularity": 0,
              "source": "BBC",
              "source_url": "http://www.bbc.co.uk/music/reviews/3vfd",
              "text": "TEXT CONTENT OF REVIEW",
              "rating": 5,
              "user": {
                "created": "Wed, 07 May 2014 14:55:23 GMT",
                "display_name": "Paul Clarke",
                "id": "f5857a65-1eb1-4574-8843-ae6195de16fa",
                "karma": 0,
                "user_type": "Noob"
              },
              "votes": {
                "positive": 0,
                "negative": 0
              }
            },
            -- more reviews here --
          }
        }

    :statuscode 200: no error
    :resheader Content-Type: *application/json*
    """
    # retrieve UUID's as list from URL parameter
    review_ids = request.args.get("review_ids")
    if not review_ids:
        return jsonify(review={})
    reviews = db_review.get_by_ids(review_ids.split(","))
    results = {
        str(review["id"]): db_review.to_dict(review)
            for review in reviews
            if not review["is_hidden"]
    }
    return jsonify(reviews=results)
