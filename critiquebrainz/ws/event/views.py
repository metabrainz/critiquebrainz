from flask import Blueprint, jsonify
import critiquebrainz.db.review as db_review
import critiquebrainz.db.rating_stats as db_rating_stats
from critiquebrainz.frontend.external.musicbrainz_db import event as db_event
from critiquebrainz.decorators import crossdomain
from critiquebrainz.ws.exceptions import NotFound
from critiquebrainz.ws.parser import Parser
from critiquebrainz.ws import REVIEWS_LIMIT
from critiquebrainz.ws import REVIEWS_LIMIT, REVIEW_CACHE_NAMESPACE, REVIEW_CACHE_TIMEOUT
from brainzutils import cache

event_bp = Blueprint('ws_event', __name__)


@event_bp.route('/<uuid:event_mbid>', methods=['GET', 'OPTIONS'])
@crossdomain(headers="Authorization, Content-Type")
def event_entity_handler(event_mbid):
    """Get list of reviews.

    **Request Example:**

    .. code-block:: bash

        $ curl "https://critiquebrainz.org/ws/1/event/3f0b7c79-1d66-40d2-a8a0-54be9ca2b18c" \\
                -X GET

    **Response Example:**

    .. code-block:: json

    {
        "average_rating": 0,
        "event": {
            "artist-rels": [
                {
                    "artist": {
                        "life-span": {
                            "begin": "1989-12-13"
                        },
                        "mbid": "20244d07-534f-4eff-b4d4-930878889970",
                        "name": "Taylor Swift",
                        "sort_name": "Swift, Taylor",
                        "type": "Person"
                    },
                    "begin-year": null,
                    "direction": "backward",
                    "end-year": null,
                    "type": "main performer",
                    "type-id": "936c7c95-3156-3889-a062-8a0cd57f8946"
                },
                {
                    "artist": {
                        "life-span": {
                            "begin": "1989-12-13"
                        },
                        "mbid": "20244d07-534f-4eff-b4d4-930878889970",
                        "name": "Taylor Swift",
                        "sort_name": "Swift, Taylor",
                        "type": "Person"
                    },
                    "begin-year": null,
                    "direction": "backward",
                    "end-year": null,
                    "type": "main performer",
                    "type-id": "936c7c95-3156-3889-a062-8a0cd57f8946"
                },
                {
                    "artist": {
                        "life-span": {
                            "begin": "1989-12-13"
                        },
                        "mbid": "20244d07-534f-4eff-b4d4-930878889970",
                        "name": "Taylor Swift",
                        "sort_name": "Swift, Taylor",
                        "type": "Person"
                    },
                    "begin-year": null,
                    "direction": "backward",
                    "end-year": null,
                    "type": "main performer",
                    "type-id": "936c7c95-3156-3889-a062-8a0cd57f8946"
                }
            ],
            "life-span": {
                "begin": "2015-05-05",
                "end": "2015-12-12"
            },
            "mbid": "3f0b7c79-1d66-40d2-a8a0-54be9ca2b18c",
            "name": "The 1989 World Tour by Taylor Swift",
            "type": "Concert"
        },
        "latest_reviews": [
            {
                "created": "Sun, 24 Jan 2016 16:46:47 GMT",
                "edits": 0,
                "entity_id": "3f0b7c79-1d66-40d2-a8a0-54be9ca2b18c",
                "entity_type": "event",
                "full_name": "Creative Commons Attribution-ShareAlike 3.0 Unported",
                "id": "1da0c290-2c8c-47b4-9703-b172aaf9576f",
                "info_url": "https://creativecommons.org/licenses/by-sa/3.0/",
                "is_draft": false,
                "is_hidden": false,
                "language": "en",
                "last_revision": {
                    "id": 9753,
                    "rating": null,
                    "review_id": "1da0c290-2c8c-47b4-9703-b172aaf9576f",
                    "text": "I had never been to a concert before, so when my mom told me that she had snagged tickets to see Taylor Swift's 1989 tour, I was speechless, anxious, overwhelmingly excited, and eager. I didn't know what to expect, but I knew Taylor was known for singing amazingly live and the numerous guest stars and the pretty costumes, lights, and scenes.\r\n\r\nBoy, was I right. The night was surely a night that I will never forget. Taylor started off with \"Welcome to New York\", one of my favorites, and continued onto some other gems of her album such as \"The New Romantics\" and \"Blank Space. I definitely was one of the embarrassing screaming girls that you always see in the audience. But everyone in the crowd was singing along to the lyrics of her new platinum album (how could you not?) and danced as she belted and strutted around the stage.\r\n\r\nTaylor Swift continued onto some of her older songs of previous years like \"I Know You Were Trouble\" and \"Mean.\" I loved them just as much! Her voice was so beautiful as the night continued. I wonder how someone could be so talented of that caliber - to be able to sing and dance for hours on end. In between tracks, she would thank the crowd and express her gratitude of being able to perform for us all. She ended the night with a bang, singing some of her classic hits like \"Love Story\" and \"We Are Never Getting Back Together.\"\r\n\r\nUltimately, one of the most momentous occasions I have ever experienced. I can't speak for other artists, but Taylor really felt the energy of the crowd and maintained that vigorous happy energy and she smiled and sang and just looked like she was having so much fun.",
                    "timestamp": "Sun, 24 Jan 2016 16:46:47 GMT"
                },
                "last_updated": "Sun, 24 Jan 2016 16:46:47 GMT",
                "license_id": "CC BY-SA 3.0",
                "popularity": 1,
                "published_on": "Sun, 24 Jan 2016 16:46:47 GMT",
                "rating": null,
                "source": null,
                "source_url": null,
                "text": "I had never been to a concert before, so when my mom told me that she had snagged tickets to see Taylor Swift's 1989 tour, I was speechless, anxious, overwhelmingly excited, and eager. I didn't know what to expect, but I knew Taylor was known for singing amazingly live and the numerous guest stars and the pretty costumes, lights, and scenes.\r\n\r\nBoy, was I right. The night was surely a night that I will never forget. Taylor started off with \"Welcome to New York\", one of my favorites, and continued onto some other gems of her album such as \"The New Romantics\" and \"Blank Space. I definitely was one of the embarrassing screaming girls that you always see in the audience. But everyone in the crowd was singing along to the lyrics of her new platinum album (how could you not?) and danced as she belted and strutted around the stage.\r\n\r\nTaylor Swift continued onto some of her older songs of previous years like \"I Know You Were Trouble\" and \"Mean.\" I loved them just as much! Her voice was so beautiful as the night continued. I wonder how someone could be so talented of that caliber - to be able to sing and dance for hours on end. In between tracks, she would thank the crowd and express her gratitude of being able to perform for us all. She ended the night with a bang, singing some of her classic hits like \"Love Story\" and \"We Are Never Getting Back Together.\"\r\n\r\nUltimately, one of the most momentous occasions I have ever experienced. I can't speak for other artists, but Taylor really felt the energy of the crowd and maintained that vigorous happy energy and she smiled and sang and just looked like she was having so much fun.",
                "user": {
                    "created": "Sun, 24 Jan 2016 16:33:34 GMT",
                    "display_name": "michelletu",
                    "id": "8f5deaf3-84b9-4024-8751-6dbc0f9cf4ef",
                    "karma": 1,
                    "user_type": "Noob"
                },
                "votes_negative_count": 0,
                "votes_positive_count": 1
            },
            {
                "created": "Sun, 17 Jan 2016 10:02:06 GMT",
                "edits": 0,
                "entity_id": "3f0b7c79-1d66-40d2-a8a0-54be9ca2b18c",
                "entity_type": "event",
                "full_name": "Creative Commons Attribution-ShareAlike 3.0 Unported",
                "id": "b02b8836-d7e2-4077-9443-38c0c0f6725f",
                "info_url": "https://creativecommons.org/licenses/by-sa/3.0/",
                "is_draft": false,
                "is_hidden": false,
                "language": "en",
                "last_revision": {
                    "id": 9636,
                    "rating": null,
                    "review_id": "b02b8836-d7e2-4077-9443-38c0c0f6725f",
                    "text": "It was one of the most hyped up music event of the year, and it certainly lived up to expectations. When it was announced that Taylor Swift would be bringing her 1989 World Tour to Singapore in November, I, among many others, made a mad rush to grab at whatever tickets we could. On the grand day itself, we were treated to a musical feast at the Singapore Indoor Stadium, which was truly an unforgettable experience. \r\n\r\nTaylor Swift started off her concert with a rousing medley of songs (\"Welcome to New York\", \"The New Romantics\" and \"Blank Space) from her platinum release album 1989, which certainly did not fail to wow the crowd. However, what made Taylor Swift's songs different this time round was that she added a Singapore touch to them, thus resonating with Singaporeans at her concert. For instance, during her dynamic single \"Blank Space\", Taylor used a metal rod to strike a pole situated in the middle of the runway, looping her saying \"Singapore\" into the backing track. \r\n\r\nNext, Taylor belted out classics from her previous albums, such as \"I Knew You Were Trouble\" and \"I Wish You Would\". In between the singles, Taylor thanked everyone at the concert for supporting her latest album \"1989\", which brought the crowd roaring with excitement. \"How You Get the Girl\" and \"You Belong With Me\" were up next, with the audience singing along to the classics. \r\n\r\nSome of her biggest hits were also subjected to makeovers. With Taylor strumming a white electric guitar, \"We Are Never Ever Getting Back Together\" sounded much heftier than the recorded version. Taylor also slowed down classics \"I Knew You Were Trouble\" and \"Love Story\" by a notch, creating a new dimension for familiar tunes. \r\n\r\nHowever, there were a couple of minor disappointments at the concert. Prior to the concert, many made wild guesses as to who the surprise guests at the Singapore concert would be - after all, Taylor had been making headlines for inviting her celebrity friends to join her in the 1989 World Tour. Hence, when we realised that there were not going to be any surprise guests, we could not help but feel a little shortchanged. But Taylor's last song for the concert, \"Shake It Off\", immediately helped us feel much better, with almost everyone jumping to their feet to dance along with Taylor, who was strutting her moves on the runway. \r\n\r\nAll in all, it was a dynamic night at the Singapore Indoor Stadium, with Taylor Swift belting out song after song, from classics to singles from her latest album. \r\n",
                    "timestamp": "Mon, 18 Jan 2016 22:52:28 GMT"
                },
                "last_updated": "Mon, 18 Jan 2016 22:52:28 GMT",
                "license_id": "CC BY-SA 3.0",
                "popularity": 0,
                "published_on": "Mon, 18 Jan 2016 22:52:28 GMT",
                "rating": null,
                "source": null,
                "source_url": null,
                "text": "It was one of the most hyped up music event of the year, and it certainly lived up to expectations. When it was announced that Taylor Swift would be bringing her 1989 World Tour to Singapore in November, I, among many others, made a mad rush to grab at whatever tickets we could. On the grand day itself, we were treated to a musical feast at the Singapore Indoor Stadium, which was truly an unforgettable experience. \r\n\r\nTaylor Swift started off her concert with a rousing medley of songs (\"Welcome to New York\", \"The New Romantics\" and \"Blank Space) from her platinum release album 1989, which certainly did not fail to wow the crowd. However, what made Taylor Swift's songs different this time round was that she added a Singapore touch to them, thus resonating with Singaporeans at her concert. For instance, during her dynamic single \"Blank Space\", Taylor used a metal rod to strike a pole situated in the middle of the runway, looping her saying \"Singapore\" into the backing track. \r\n\r\nNext, Taylor belted out classics from her previous albums, such as \"I Knew You Were Trouble\" and \"I Wish You Would\". In between the singles, Taylor thanked everyone at the concert for supporting her latest album \"1989\", which brought the crowd roaring with excitement. \"How You Get the Girl\" and \"You Belong With Me\" were up next, with the audience singing along to the classics. \r\n\r\nSome of her biggest hits were also subjected to makeovers. With Taylor strumming a white electric guitar, \"We Are Never Ever Getting Back Together\" sounded much heftier than the recorded version. Taylor also slowed down classics \"I Knew You Were Trouble\" and \"Love Story\" by a notch, creating a new dimension for familiar tunes. \r\n\r\nHowever, there were a couple of minor disappointments at the concert. Prior to the concert, many made wild guesses as to who the surprise guests at the Singapore concert would be - after all, Taylor had been making headlines for inviting her celebrity friends to join her in the 1989 World Tour. Hence, when we realised that there were not going to be any surprise guests, we could not help but feel a little shortchanged. But Taylor's last song for the concert, \"Shake It Off\", immediately helped us feel much better, with almost everyone jumping to their feet to dance along with Taylor, who was strutting her moves on the runway. \r\n\r\nAll in all, it was a dynamic night at the Singapore Indoor Stadium, with Taylor Swift belting out song after song, from classics to singles from her latest album. \r\n",
                "user": {
                    "created": "Sun, 17 Jan 2016 06:49:23 GMT",
                    "display_name": "gabriellee",
                    "id": "172631a3-8338-4aaf-84c8-1ed0f02c56c1",
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
            "5": 0
        },
        "reviews_count": 2,
        "top_reviews": [
            {
                "created": "Sun, 24 Jan 2016 16:46:47 GMT",
                "edits": 0,
                "entity_id": "3f0b7c79-1d66-40d2-a8a0-54be9ca2b18c",
                "entity_type": "event",
                "full_name": "Creative Commons Attribution-ShareAlike 3.0 Unported",
                "id": "1da0c290-2c8c-47b4-9703-b172aaf9576f",
                "info_url": "https://creativecommons.org/licenses/by-sa/3.0/",
                "is_draft": false,
                "is_hidden": false,
                "language": "en",
                "last_revision": {
                    "id": 9753,
                    "rating": null,
                    "review_id": "1da0c290-2c8c-47b4-9703-b172aaf9576f",
                    "text": "I had never been to a concert before, so when my mom told me that she had snagged tickets to see Taylor Swift's 1989 tour, I was speechless, anxious, overwhelmingly excited, and eager. I didn't know what to expect, but I knew Taylor was known for singing amazingly live and the numerous guest stars and the pretty costumes, lights, and scenes.\r\n\r\nBoy, was I right. The night was surely a night that I will never forget. Taylor started off with \"Welcome to New York\", one of my favorites, and continued onto some other gems of her album such as \"The New Romantics\" and \"Blank Space. I definitely was one of the embarrassing screaming girls that you always see in the audience. But everyone in the crowd was singing along to the lyrics of her new platinum album (how could you not?) and danced as she belted and strutted around the stage.\r\n\r\nTaylor Swift continued onto some of her older songs of previous years like \"I Know You Were Trouble\" and \"Mean.\" I loved them just as much! Her voice was so beautiful as the night continued. I wonder how someone could be so talented of that caliber - to be able to sing and dance for hours on end. In between tracks, she would thank the crowd and express her gratitude of being able to perform for us all. She ended the night with a bang, singing some of her classic hits like \"Love Story\" and \"We Are Never Getting Back Together.\"\r\n\r\nUltimately, one of the most momentous occasions I have ever experienced. I can't speak for other artists, but Taylor really felt the energy of the crowd and maintained that vigorous happy energy and she smiled and sang and just looked like she was having so much fun.",
                    "timestamp": "Sun, 24 Jan 2016 16:46:47 GMT"
                },
                "last_updated": "Sun, 24 Jan 2016 16:46:47 GMT",
                "license_id": "CC BY-SA 3.0",
                "popularity": 1,
                "published_on": "Sun, 24 Jan 2016 16:46:47 GMT",
                "rating": null,
                "source": null,
                "source_url": null,
                "text": "I had never been to a concert before, so when my mom told me that she had snagged tickets to see Taylor Swift's 1989 tour, I was speechless, anxious, overwhelmingly excited, and eager. I didn't know what to expect, but I knew Taylor was known for singing amazingly live and the numerous guest stars and the pretty costumes, lights, and scenes.\r\n\r\nBoy, was I right. The night was surely a night that I will never forget. Taylor started off with \"Welcome to New York\", one of my favorites, and continued onto some other gems of her album such as \"The New Romantics\" and \"Blank Space. I definitely was one of the embarrassing screaming girls that you always see in the audience. But everyone in the crowd was singing along to the lyrics of her new platinum album (how could you not?) and danced as she belted and strutted around the stage.\r\n\r\nTaylor Swift continued onto some of her older songs of previous years like \"I Know You Were Trouble\" and \"Mean.\" I loved them just as much! Her voice was so beautiful as the night continued. I wonder how someone could be so talented of that caliber - to be able to sing and dance for hours on end. In between tracks, she would thank the crowd and express her gratitude of being able to perform for us all. She ended the night with a bang, singing some of her classic hits like \"Love Story\" and \"We Are Never Getting Back Together.\"\r\n\r\nUltimately, one of the most momentous occasions I have ever experienced. I can't speak for other artists, but Taylor really felt the energy of the crowd and maintained that vigorous happy energy and she smiled and sang and just looked like she was having so much fun.",
                "user": {
                    "created": "Sun, 24 Jan 2016 16:33:34 GMT",
                    "display_name": "michelletu",
                    "id": "8f5deaf3-84b9-4024-8751-6dbc0f9cf4ef",
                    "karma": 1,
                    "user_type": "Noob"
                },
                "votes_negative_count": 0,
                "votes_positive_count": 1
            },
            {
                "created": "Sun, 17 Jan 2016 10:02:06 GMT",
                "edits": 0,
                "entity_id": "3f0b7c79-1d66-40d2-a8a0-54be9ca2b18c",
                "entity_type": "event",
                "full_name": "Creative Commons Attribution-ShareAlike 3.0 Unported",
                "id": "b02b8836-d7e2-4077-9443-38c0c0f6725f",
                "info_url": "https://creativecommons.org/licenses/by-sa/3.0/",
                "is_draft": false,
                "is_hidden": false,
                "language": "en",
                "last_revision": {
                    "id": 9636,
                    "rating": null,
                    "review_id": "b02b8836-d7e2-4077-9443-38c0c0f6725f",
                    "text": "It was one of the most hyped up music event of the year, and it certainly lived up to expectations. When it was announced that Taylor Swift would be bringing her 1989 World Tour to Singapore in November, I, among many others, made a mad rush to grab at whatever tickets we could. On the grand day itself, we were treated to a musical feast at the Singapore Indoor Stadium, which was truly an unforgettable experience. \r\n\r\nTaylor Swift started off her concert with a rousing medley of songs (\"Welcome to New York\", \"The New Romantics\" and \"Blank Space) from her platinum release album 1989, which certainly did not fail to wow the crowd. However, what made Taylor Swift's songs different this time round was that she added a Singapore touch to them, thus resonating with Singaporeans at her concert. For instance, during her dynamic single \"Blank Space\", Taylor used a metal rod to strike a pole situated in the middle of the runway, looping her saying \"Singapore\" into the backing track. \r\n\r\nNext, Taylor belted out classics from her previous albums, such as \"I Knew You Were Trouble\" and \"I Wish You Would\". In between the singles, Taylor thanked everyone at the concert for supporting her latest album \"1989\", which brought the crowd roaring with excitement. \"How You Get the Girl\" and \"You Belong With Me\" were up next, with the audience singing along to the classics. \r\n\r\nSome of her biggest hits were also subjected to makeovers. With Taylor strumming a white electric guitar, \"We Are Never Ever Getting Back Together\" sounded much heftier than the recorded version. Taylor also slowed down classics \"I Knew You Were Trouble\" and \"Love Story\" by a notch, creating a new dimension for familiar tunes. \r\n\r\nHowever, there were a couple of minor disappointments at the concert. Prior to the concert, many made wild guesses as to who the surprise guests at the Singapore concert would be - after all, Taylor had been making headlines for inviting her celebrity friends to join her in the 1989 World Tour. Hence, when we realised that there were not going to be any surprise guests, we could not help but feel a little shortchanged. But Taylor's last song for the concert, \"Shake It Off\", immediately helped us feel much better, with almost everyone jumping to their feet to dance along with Taylor, who was strutting her moves on the runway. \r\n\r\nAll in all, it was a dynamic night at the Singapore Indoor Stadium, with Taylor Swift belting out song after song, from classics to singles from her latest album. \r\n",
                    "timestamp": "Mon, 18 Jan 2016 22:52:28 GMT"
                },
                "last_updated": "Mon, 18 Jan 2016 22:52:28 GMT",
                "license_id": "CC BY-SA 3.0",
                "popularity": 0,
                "published_on": "Mon, 18 Jan 2016 22:52:28 GMT",
                "rating": null,
                "source": null,
                "source_url": null,
                "text": "It was one of the most hyped up music event of the year, and it certainly lived up to expectations. When it was announced that Taylor Swift would be bringing her 1989 World Tour to Singapore in November, I, among many others, made a mad rush to grab at whatever tickets we could. On the grand day itself, we were treated to a musical feast at the Singapore Indoor Stadium, which was truly an unforgettable experience. \r\n\r\nTaylor Swift started off her concert with a rousing medley of songs (\"Welcome to New York\", \"The New Romantics\" and \"Blank Space) from her platinum release album 1989, which certainly did not fail to wow the crowd. However, what made Taylor Swift's songs different this time round was that she added a Singapore touch to them, thus resonating with Singaporeans at her concert. For instance, during her dynamic single \"Blank Space\", Taylor used a metal rod to strike a pole situated in the middle of the runway, looping her saying \"Singapore\" into the backing track. \r\n\r\nNext, Taylor belted out classics from her previous albums, such as \"I Knew You Were Trouble\" and \"I Wish You Would\". In between the singles, Taylor thanked everyone at the concert for supporting her latest album \"1989\", which brought the crowd roaring with excitement. \"How You Get the Girl\" and \"You Belong With Me\" were up next, with the audience singing along to the classics. \r\n\r\nSome of her biggest hits were also subjected to makeovers. With Taylor strumming a white electric guitar, \"We Are Never Ever Getting Back Together\" sounded much heftier than the recorded version. Taylor also slowed down classics \"I Knew You Were Trouble\" and \"Love Story\" by a notch, creating a new dimension for familiar tunes. \r\n\r\nHowever, there were a couple of minor disappointments at the concert. Prior to the concert, many made wild guesses as to who the surprise guests at the Singapore concert would be - after all, Taylor had been making headlines for inviting her celebrity friends to join her in the 1989 World Tour. Hence, when we realised that there were not going to be any surprise guests, we could not help but feel a little shortchanged. But Taylor's last song for the concert, \"Shake It Off\", immediately helped us feel much better, with almost everyone jumping to their feet to dance along with Taylor, who was strutting her moves on the runway. \r\n\r\nAll in all, it was a dynamic night at the Singapore Indoor Stadium, with Taylor Swift belting out song after song, from classics to singles from her latest album. \r\n",
                "user": {
                    "created": "Sun, 17 Jan 2016 06:49:23 GMT",
                    "display_name": "gabriellee",
                    "id": "172631a3-8338-4aaf-84c8-1ed0f02c56c1",
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

    :resheader Content-Type: *application/json*
    """

    event = db_event.get_event_by_mbid(str(event_mbid))

    if not event:
        raise NotFound("Can't find an event with ID: {event_mbid}".format(event_mbid=event_mbid))

    user_review = None

    user_id = Parser.uuid('uri', 'user_id', optional=True)
    if user_id:
        user_review_cache_key = cache.gen_key('entity_api', event['mbid'], user_id, "user_review")
        user_review = cache.get(user_review_cache_key)
        if not user_review:
            user_review, _ = db_review.list_reviews(
                entity_id=event['mbid'],
                entity_type='event',
                user_id=user_id
            )
            if user_review:
                user_review = db_review.to_dict(user_review[0])
            else:
                user_review = None

            cache.set(user_review_cache_key, user_review,
                expirein=REVIEW_CACHE_TIMEOUT, namespace=REVIEW_CACHE_NAMESPACE)

    ratings_stats, average_rating = db_rating_stats.get_stats(event_mbid, "event")

    top_reviews_cache_key = cache.gen_key("entity_api_event", event['mbid'], "top_reviews")
    top_reviews_cached_result = cache.get(top_reviews_cache_key, REVIEW_CACHE_NAMESPACE)

    if top_reviews_cached_result:
        top_reviews, reviews_count = top_reviews_cached_result
    else:
        top_reviews, reviews_count = db_review.list_reviews(
            entity_id=event['mbid'],
            entity_type='event',
            sort='popularity',
            limit=REVIEWS_LIMIT,
            offset=0,
        )
        top_reviews = [db_review.to_dict(review) for review in top_reviews]

        cache.set(top_reviews_cache_key, (top_reviews, reviews_count),
                  expirein=REVIEW_CACHE_TIMEOUT, namespace=REVIEW_CACHE_NAMESPACE)

    latest_reviews_cache_key = cache.gen_key("entity_api_event", event['mbid'], "latest_reviews")
    latest_reviews_cached_result = cache.get(latest_reviews_cache_key, REVIEW_CACHE_NAMESPACE)

    if latest_reviews_cached_result:
        latest_reviews, reviews_count = latest_reviews_cached_result
    else:
        latest_reviews, reviews_count = db_review.list_reviews(
            entity_id=event['mbid'],
            entity_type='event',
            sort='published_on',
            limit=REVIEWS_LIMIT,
            offset=0,
        )
        latest_reviews = [db_review.to_dict(review) for review in latest_reviews]

        cache.set(latest_reviews_cache_key, (latest_reviews, reviews_count),
                  expirein=REVIEW_CACHE_TIMEOUT, namespace=REVIEW_CACHE_NAMESPACE)

    result = {
        "event": event,
        "average_rating": average_rating,
        "ratings_stats": ratings_stats,
        "reviews_count": reviews_count,
        "top_reviews": top_reviews,
        "latest_reviews": latest_reviews
    }
    if user_id:
        result['user_review'] = user_review

    return jsonify(**result)
