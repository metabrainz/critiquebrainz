from flask_wtf import FlaskForm
from flask_babel import lazy_gettext
from wtforms import TextAreaField, StringField
from wtforms.widgets import HiddenInput
from wtforms.validators import Length


class CommentEditForm(FlaskForm):
    state = StringField(widget=HiddenInput(), default='publish')
    text = TextAreaField(
        lazy_gettext("Add a comment..."),
        validators=[Length(min= 1, message=lazy_gettext("Comment must not be empty!"))]
    )
    review_id = StringField(widget=HiddenInput())

    def __init__(self, review_id=None, **kwargs):
        kwargs['review_id'] = review_id
        FlaskForm.__init__(self, **kwargs)
