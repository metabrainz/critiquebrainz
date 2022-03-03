from flask import Blueprint, jsonify
import critiquebrainz.db.review as db_review
import critiquebrainz.db.rating_stats as db_rating_stats
from critiquebrainz.db import exceptions as db_exceptions
import critiquebrainz.frontend.external.musicbrainz_db.artist as mb_artist
from brainzutils.musicbrainz_db import artist as db_artist
from critiquebrainz.decorators import crossdomain
from critiquebrainz.ws.exceptions import NotFound

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
                "id": "b7d92248-97e3-4450-8057-6fe06738f735", 
                "name": "Shawn Mendes", 
                "sort_name": "Mendes, Shawn", 
                "type": "Person"
            }, 
            "avg_rating": 5.0, 
            "latest_reviews": [
                {
                "created": "Mon, 24 Jan 2022 18:11:59 GMT", 
                "edits": 0, 
                "entity_id": "b7d92248-97e3-4450-8057-6fe06738f735", 
                "entity_type": "artist", 
                "full_name": "Creative Commons Attribution-ShareAlike 3.0 Unported", 
                "id": "89fb94fd-3e65-4e52-8d16-5bdca4572883", 
                "info_url": "https://creativecommons.org/licenses/by-sa/3.0/", 
                "is_draft": false, 
                "is_hidden": false, 
                "language": "en", 
                "last_revision": {
                    "id": 11258, 
                    "rating": 5, 
                    "review_id": "89fb94fd-3e65-4e52-8d16-5bdca4572883", 
                    "text": null, 
                    "timestamp": "Mon, 24 Jan 2022 18:11:59 GMT"
                }, 
                "last_updated": "Mon, 24 Jan 2022 18:11:59 GMT", 
                "license_id": "CC BY-SA 3.0", 
                "popularity": 0, 
                "published_on": "Mon, 24 Jan 2022 18:11:59 GMT", 
                "rating": 5, 
                "source": null, 
                "source_url": null, 
                "text": null, 
                "user": {
                    "created": "Sun, 23 Jan 2022 15:17:48 GMT", 
                    "display_name": "Ashutosh Aswal", 
                    "id": "36b854f0-8601-4eab-8e59-3733e7f8de24", 
                    "karma": 0, 
                    "user_type": "Noob"
                }, 
                "votes_negative_count": 0, 
                "votes_positive_count": 0
                }, 
                {
                "created": "Thu, 27 Jan 2022 16:54:09 GMT", 
                "edits": 0, 
                "entity_id": "b7d92248-97e3-4450-8057-6fe06738f735", 
                "entity_type": "artist", 
                "full_name": "Creative Commons Attribution-ShareAlike 3.0 Unported", 
                "id": "d326c9d2-1e4c-448d-be05-5f6cd872de0d", 
                "info_url": "https://creativecommons.org/licenses/by-sa/3.0/", 
                "is_draft": false, 
                "is_hidden": false, 
                "language": "en", 
                "last_revision": {
                    "id": 11265, 
                    "rating": 5, 
                    "review_id": "d326c9d2-1e4c-448d-be05-5f6cd872de0d", 
                    "text": null, 
                    "timestamp": "Thu, 27 Jan 2022 16:54:09 GMT"
                }, 
                "last_updated": "Thu, 27 Jan 2022 16:54:09 GMT", 
                "license_id": "CC BY-SA 3.0", 
                "popularity": 0, 
                "published_on": "Thu, 27 Jan 2022 16:54:09 GMT", 
                "rating": 5, 
                "source": null, 
                "source_url": null, 
                "text": null, 
                "user": {
                    "created": "Sat, 09 Feb 2019 13:06:27 GMT", 
                    "display_name": "amCap1712", 
                    "id": "23f97b7f-3ea3-4557-b808-1cb08474b28b", 
                    "karma": 0, 
                    "user_type": "Noob"
                }, 
                "votes_negative_count": 0, 
                "votes_positive_count": 0
                }
            ], 
            "rating_stats": {
                "1": 0, 
                "2": 0, 
                "3": 0, 
                "4": 0, 
                "5": 2
            }, 
            "reviews_count": 2, 
            "top_reviews": [
                {
                "created": "Mon, 24 Jan 2022 18:11:59 GMT", 
                "edits": 0, 
                "entity_id": "b7d92248-97e3-4450-8057-6fe06738f735", 
                "entity_type": "artist", 
                "full_name": "Creative Commons Attribution-ShareAlike 3.0 Unported", 
                "id": "89fb94fd-3e65-4e52-8d16-5bdca4572883", 
                "info_url": "https://creativecommons.org/licenses/by-sa/3.0/", 
                "is_draft": false, 
                "is_hidden": false, 
                "language": "en", 
                "last_revision": {
                    "id": 11258, 
                    "rating": 5, 
                    "review_id": "89fb94fd-3e65-4e52-8d16-5bdca4572883", 
                    "text": null, 
                    "timestamp": "Mon, 24 Jan 2022 18:11:59 GMT"
                }, 
                "last_updated": "Mon, 24 Jan 2022 18:11:59 GMT", 
                "license_id": "CC BY-SA 3.0", 
                "popularity": 0, 
                "published_on": "Mon, 24 Jan 2022 18:11:59 GMT", 
                "rating": 5, 
                "source": null, 
                "source_url": null, 
                "text": null, 
                "user": {
                    "created": "Sun, 23 Jan 2022 15:17:48 GMT", 
                    "display_name": "Ashutosh Aswal", 
                    "id": "36b854f0-8601-4eab-8e59-3733e7f8de24", 
                    "karma": 0, 
                    "user_type": "Noob"
                }, 
                "votes_negative_count": 0, 
                "votes_positive_count": 0
                }, 
                {
                "created": "Thu, 27 Jan 2022 16:54:09 GMT", 
                "edits": 0, 
                "entity_id": "b7d92248-97e3-4450-8057-6fe06738f735", 
                "entity_type": "artist", 
                "full_name": "Creative Commons Attribution-ShareAlike 3.0 Unported", 
                "id": "d326c9d2-1e4c-448d-be05-5f6cd872de0d", 
                "info_url": "https://creativecommons.org/licenses/by-sa/3.0/", 
                "is_draft": false, 
                "is_hidden": false, 
                "language": "en", 
                "last_revision": {
                    "id": 11265, 
                    "rating": 5, 
                    "review_id": "d326c9d2-1e4c-448d-be05-5f6cd872de0d", 
                    "text": null, 
                    "timestamp": "Thu, 27 Jan 2022 16:54:09 GMT"
                }, 
                "last_updated": "Thu, 27 Jan 2022 16:54:09 GMT", 
                "license_id": "CC BY-SA 3.0", 
                "popularity": 0, 
                "published_on": "Thu, 27 Jan 2022 16:54:09 GMT", 
                "rating": 5, 
                "source": null, 
                "source_url": null, 
                "text": null, 
                "user": {
                    "created": "Sat, 09 Feb 2019 13:06:27 GMT", 
                    "display_name": "amCap1712", 
                    "id": "23f97b7f-3ea3-4557-b808-1cb08474b28b", 
                    "karma": 0, 
                    "user_type": "Noob"
                }, 
                "votes_negative_count": 0, 
                "votes_positive_count": 0
                }
            ]
        }

    :statuscode 200: no error
    :statuscode 404: review not found
    
    :resheader Content-Type: *application/json*
    """

    try:
        artist = db_artist.get_artist_by_id(str(artist_mbid))
    except db_exceptions.NoDataFoundException:
        raise NotFound("Can't find an artist with ID: {artist_mbid}".format(artist_mbid=artist_mbid))

    ratings_stats, average_rating = db_rating_stats.get_stats(artist_mbid, "artist")

    reviews_limit = 5

    top_reviews, reviews_count = db_review.list_reviews(
        entity_id=artist['id'],
        entity_type='artist',
        sort='popularity',
        limit=reviews_limit,
        offset=0,
    )

    latest_reviews, reviews_count = db_review.list_reviews(
        entity_id=artist['id'],
        entity_type='artist',
        sort='popularity',
        limit=reviews_limit,
        offset=0,
    )
    
    top_reviews = [db_review.to_dict(p) for p in top_reviews]
    latest_reviews = [db_review.to_dict(p) for p in latest_reviews]

    return jsonify(artist=artist, avg_rating=average_rating, rating_stats=ratings_stats, reviews_count=reviews_count, top_reviews=top_reviews, latest_reviews=latest_reviews)
