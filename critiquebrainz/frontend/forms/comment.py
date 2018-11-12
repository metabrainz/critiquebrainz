from flask_babel import lazy_gettext
from flask_wtf import Form
from wtforms import TextAreaField, StringField
from wtforms.widgets import HiddenInput
from wtforms.validators import DataRequired


class CommentEditForm(Form):
    state = StringField(widget=HiddenInput(), default='publish')
    text = TextAreaField(lazy_gettext("Add a comment..."), validators=[DataRequired()])
    review_id = StringField(widget=HiddenInput())

    def __init__(self, review_id=None, **kwargs):
        kwargs['review_id'] = review_id
        Form.__init__(self, **kwargs)
