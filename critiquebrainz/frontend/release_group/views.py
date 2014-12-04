from flask import Blueprint, render_template, request
from flask_login import current_user
from flask_babel import gettext
from critiquebrainz.frontend.apis import musicbrainz, mbspotify
from critiquebrainz.frontend.exceptions import NotFound
from critiquebrainz.data.model.review import Review


release_group_bp = Blueprint('release_group', __name__)


@release_group_bp.route('/<uuid:id>')
def entity(id):
    id = str(id)
    release_group = musicbrainz.get_release_group_by_id(id)
    if not release_group:
        raise NotFound(gettext("Sorry, we couldn't find a release group with that MusicBrainz ID."))
    if len(release_group['release-list']) > 0:
        release = musicbrainz.get_release_by_id(release_group['release-list'][0]['id'])
    else:
        release = None
    spotify_mappings = mbspotify.mappings(id)
    limit = int(request.args.get('limit', default=10))
    offset = int(request.args.get('offset', default=0))
    if current_user.is_authenticated():
        my_reviews, my_count = Review.list(release_group=id, user_id=current_user.id)
        if my_count != 0:
            my_review = my_reviews[0]
        else:
            my_review = None
    else:
        my_review = None
    reviews, count = Review.list(release_group=id, sort='rating', limit=limit, offset=offset)
    return render_template('release_group.html', id=id, release_group=release_group, reviews=reviews,
                           release=release, my_review=my_review, spotify_mappings=spotify_mappings,
                           limit=limit, offset=offset, count=count)
