from flask import Blueprint, render_template, request
from flask_login import current_user
from flask_babel import gettext
from critiquebrainz.frontend.external import musicbrainz, mbspotify, soundcloud
from critiquebrainz.data.model.review import Review
from werkzeug.exceptions import NotFound


release_group_bp = Blueprint('release_group', __name__)


@release_group_bp.route('/<uuid:id>')
def entity(id):
    id = str(id)
    release_group = musicbrainz.get_release_group_by_id(id)
    if not release_group:
        raise NotFound(gettext("Sorry, we couldn't find a release group with that MusicBrainz ID."))
    if 'tag-list' in release_group:
        tags = release_group['tag-list']
    else:
        tags = None
    if len(release_group['release-list']) > 0:
        release = musicbrainz.get_release_by_id(release_group['release-list'][0]['id'])
    else:
        release = None
    soundcloud_url = soundcloud.get_url(id)
    if soundcloud_url:
        spotify_mappings = None
    else:
        spotify_mappings = mbspotify.mappings(id)
    limit = int(request.args.get('limit', default=10))
    offset = int(request.args.get('offset', default=0))
    if current_user.is_authenticated:
        my_reviews, my_count = Review.list(entity_id=id, entity_type='release_group', user_id=current_user.id)
        if my_count != 0:
            my_review = my_reviews[0]
        else:
            my_review = None
    else:
        my_review = None
    reviews, count = Review.list(entity_id=id, entity_type='release_group', sort='rating', limit=limit, offset=offset)
    return render_template('release_group/entity.html', id=id, release_group=release_group, reviews=reviews,
                           release=release, my_review=my_review, spotify_mappings=spotify_mappings, tags=tags,
                           soundcloud_url=soundcloud_url, limit=limit, offset=offset, count=count)
