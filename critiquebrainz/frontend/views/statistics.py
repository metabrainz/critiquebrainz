# critiquebrainz - Repository for Creative Commons licensed reviews
#
# Copyright (C) 2019 Bimalkant Lauhny.
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
import critiquebrainz.db.statistics as db_statistics

statistics_bp = Blueprint('statistics', __name__)


@statistics_bp.route('/')
def statistics():
    top_users_overall = db_statistics.get_top_users_overall()
    return render_template(
        'statistics/stats.html',
        top_users_overall=top_users_overall,
    )
