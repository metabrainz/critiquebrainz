from flask import Blueprint, render_template, request
from flask.ext.login import current_user
from flask.ext.babel import gettext

from critiquebrainz.apis import server, musicbrainz, mbspotify
from critiquebrainz.exceptions import NotFound

bp = Blueprint('release_group', __name__)


@bp.route('/<uuid:id>', endpoint='entity')
def release_group_entity_handler(id):
    release_group = musicbrainz.get_release_group_by_id(id, includes=['artists', 'releases',
                                                                      'release-group-rels', 'url-rels', 'work-rels'])
    if not release_group:
        raise NotFound(gettext("Sorry we couldn't find release group with that MusicBrainz ID."))
    if len(release_group['release-list']) > 0:
        release = musicbrainz.get_release_by_id(release_group['release-list'][0]['id'], includes=['recordings'])
    else:
        release = None
    spotify_mapping = mbspotify.mapping([str(id)])
    limit = int(request.args.get('limit', default=10))
    offset = int(request.args.get('offset', default=0))
    if hasattr(current_user, 'me'):
        my_count, my_reviews = server.get_reviews(release_group=id, user_id=current_user.me['id'])
        if my_count != 0:
            my_review = my_reviews[0]
        else:
            my_review = None
    else:
        my_review = None
    count, reviews = server.get_reviews(release_group=id, sort='created',
                                        limit=limit, offset=offset, inc=['user'])
    return render_template('release_group.html', id=str(id), release_group=release_group, reviews=reviews,
                           release=release, my_review=my_review, spotify_mapping=spotify_mapping,
                           limit=limit, offset=offset, count=count)
