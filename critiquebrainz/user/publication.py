from flask import Blueprint, render_template
from flask.ext.login import login_required, current_user
from critiquebrainz.db import Publication

publication = Blueprint('ui_publication', __name__)

@publication.route('/album', endpoint='album')
@login_required
def publication_album_handler():
    return render_template('user/publication/album/list.html',
        publications=current_user.publications)

@publication.route('/delete/<uuid:publication_id>', endpoint='delete')
@login_required
def publication_delete_handler(publication_id):
    pass
