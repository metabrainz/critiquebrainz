from flask import Blueprint, render_template, request
from flask_login import current_user
from flask_babel import gettext
from critiquebrainz.frontend.external import mbspotify, soundcloud
import critiquebrainz.frontend.external.musicbrainz_db.release_group as mb_release_group
import critiquebrainz.frontend.external.musicbrainz_db.exceptions as mb_exceptions
import critiquebrainz.frontend.external.musicbrainz_db.release as mb_release
import critiquebrainz.db.review as db_review
from critiquebrainz.frontend.views import get_avg_rating
from werkzeug.exceptions import NotFound


release_group_bp = Blueprint('release_group', __name__)


@release_group_bp.route('/<uuid:id>')
def entity(id):
    id = str(id)
    try:
        release_group = mb_release_group.get_release_group_by_id(id)
    except mb_exceptions.NoDataFoundException:
        raise NotFound(gettext("Sorry, we couldn't find a release group with that MusicBrainz ID."))

    if 'tag-list' in release_group:
        tags = release_group['tag-list']
    else:
        tags = None
    if 'release-list' in release_group and release_group['release-list']:
        release = mb_release.get_release_by_id(release_group['release-list'][0]['id'])
    else:
        release = None
    soundcloud_url = soundcloud.get_url(release_group['id'])
    if soundcloud_url:
        spotify_mappings = None
    else:
        spotify_mappings = mbspotify.mappings(release_group['id'])
    limit = int(request.args.get('limit', default=10))
    offset = int(request.args.get('offset', default=0))
    if current_user.is_authenticated:
        my_reviews, my_count = db_review.list_reviews(
            entity_id=release_group['id'],
            entity_type='release_group',
            user_id=current_user.id,
        )
        if my_count != 0:
            my_review = my_reviews[0]
        else:
            my_review = None
    else:
        my_review = None
    reviews, count = db_review.list_reviews(
        entity_id=release_group['id'],
        entity_type='release_group',
        sort='popularity',
        limit=limit,
        offset=offset,
    )
    avg_rating = get_avg_rating(release_group['id'], "release_group")

    return render_template('release_group/entity.html', id=release_group['id'], release_group=release_group, reviews=reviews,
                           release=release, my_review=my_review, spotify_mappings=spotify_mappings, tags=tags,
                           soundcloud_url=soundcloud_url, limit=limit, offset=offset, count=count, avg_rating=avg_rating)
