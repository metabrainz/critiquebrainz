import uuid

from flask import Blueprint, jsonify, request

from critiquebrainz.decorators import crossdomain
from critiquebrainz.ws.exceptions import InvalidRequest
import critiquebrainz.db.review as db_review

bulk_review_bp = Blueprint('ws_review_bulk', __name__)

MAX_ITEMS_PER_BULK_REQUEST = 25


def remove_duplicates(arr):
    seen = set()
    return [x for x in arr if not (x in seen or seen.add(x))]


def _validate_bulk_params(review_ids):
    """
    Validate a string containing a comma separated list of review uuids.
    If any item in the list is an invalid uuid (even if there are other valid ones) then raise
      cb.ws.exceptions.InvalidRequest
    If any item in the list is empty (e.g. uuid,,uuid) then silently skip it.
    If any item in the list is duplicated then only return one
    If any item in the list is a valid uuid but malformed (e.g. separating - placed in the wrong place, or letters
      in upper-case instead of lower-case) then return a correctly formatted version of the uuid, and return
      a mapping of the user-provided uuid -> formatted uuid in review_id_mapping

    Arguments:
        review_ids: a comma separated string of review uuids

    Returns:
        A tuple (review_ids, review_id_mapping) where review_ids is a unique list of formatted uuids, and
        review_id_mapping maps user-provided uuid values to formatted uuids

    Raises:
        critiquebrainz.ws.exceptions.InvalidRequest: if any provided argument isn't a valid uuid, or if
          more than MAX_ITEMS_PER_BULK_REQUEST items are provided.
    """

    ret = []
    mbid_mapping = {}
    for mbid in review_ids.split(","):
        if not mbid:
            continue
        try:
            normalised_mbid = str(uuid.UUID(mbid))
            mbid_mapping[mbid] = normalised_mbid
        except ValueError:
            raise InvalidRequest("'review_ids' parameter includes an invalid UUID")

        ret.append(normalised_mbid)

    if len(ret) > MAX_ITEMS_PER_BULK_REQUEST:
        raise InvalidRequest(f"More than {MAX_ITEMS_PER_BULK_REQUEST} recordings not allowed per request")

    # Remove duplicates, preserving order
    return remove_duplicates(ret), mbid_mapping


@bulk_review_bp.route('/', methods=['GET', 'OPTIONS'])
@crossdomain(headers="Authorization, Content-Type")
def bulk_review_entity_handler():
    """Get a list of reviews with specified UUIDs.

       Hidden reviews are omitted from the response. UUIDs which are not valid result in an error.
       UUIDs which are not review ids are omitted from the response.

       The returned data is a dictionary where each key is the review id. This UUID is formatted in the canonical
       UUID representation and may be different from the UUID that was passed in as the query parameter.
       A mapping of user-provided UUIDs to canonical representation is provided in the ``review_id_mapping``
       element of the response.

    **Request Example:**

    .. code-block:: bash

       $ curl https://critiquebrainz.org/ws/1/reviews?review_ids=B7575C23-13D5-4ADC-AC09-2F55A647D3DE,e4364ed2-a5db-4427-8456-ea7604b499ef \\
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
          },
          "review_id_mapping": {
            "B7575C23-13D5-4ADC-AC09-2F55A647D3DE": "b7575c23-13d5-4adc-ac09-2f55a647d3de"
          }
        }

    :statuscode 200: no error
    :statuscode 400: Too many review ids were requested, or a provided review id isn't a valid UUID
    :statuscode 503: Query string is too long
    :query review_ids: a comma-separated list of review IDs to retrieve.
    :resheader Content-Type: *application/json*
    """
    review_ids = request.args.get("review_ids")
    if not review_ids:
        return jsonify(reviews={}, review_id_mapping={})

    review_ids, review_id_mapping = _validate_bulk_params(review_ids)
    reviews = db_review.get_by_ids(review_ids)

    # review_id_mapping should only include the reviews that we are returning
    # (don't return an ID that doesn't match a review, or which is for a hidden review)
    review_ret = {
        str(review["id"]): db_review.to_dict(review) for review in reviews if not review["is_hidden"]
    }
    review_id_mapping = {k: v for k, v in review_id_mapping.items() if v in review_ret}

    response = {
        "reviews": review_ret,
        "review_id_mapping": review_id_mapping
    }
    return jsonify(**response)
