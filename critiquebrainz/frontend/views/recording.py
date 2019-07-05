# critiquebrainz - Repository for Creative Commons licensed reviews
#
# Copyright (C) 2018 MetaBrainz Foundation Inc.
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License along
# with this program; if not, write to the Free Software Foundation, Inc.,
# 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301 USA.

from flask import Blueprint, render_template
# from flask import request
# from flask_login import current_user
from werkzeug.exceptions import NotFound
from flask_babel import gettext
import critiquebrainz.frontend.external.musicbrainz_db.recording as mb_recording
import critiquebrainz.frontend.external.musicbrainz_db.exceptions as mb_exceptions
# import critiquebrainz.db.review as db_review
# from critiquebrainz.frontend.forms.rate import RatingEditForm
# from critiquebrainz.frontend.views import get_avg_rating


recording_bp = Blueprint('recording', __name__)


@recording_bp.route('/<uuid:id>')
def entity(id):
    id = str(id)
    try:
        recording = mb_recording.get_recording_by_id(id)
    except mb_exceptions.NoDataFoundException:
        raise NotFound(gettext("Sorry, we couldn't find a release group with that MusicBrainz ID."))

    return render_template('recording/entity.html', id=recording['id'], recording=recording)
