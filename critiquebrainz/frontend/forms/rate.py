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

from flask_wtf import Form
from flask_babel import lazy_gettext
from wtforms import validators, IntegerField, StringField
from wtforms.widgets import Input, HiddenInput


class RatingEditForm(Form):
    rating = IntegerField(lazy_gettext("Rating"), widget=Input(input_type='number'), validators=[validators.Optional()])
    entity_id = StringField(widget=HiddenInput())
    entity_type = StringField(widget=HiddenInput())

    def __init__(self, entity_id = None, entity_type=None, **kwargs):
        kwargs['entity_id'] = entity_id
        kwargs['entity_type'] = entity_type
        Form.__init__(self, **kwargs)
