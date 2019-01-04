from flask_wtf import FlaskForm
from flask_babel import lazy_gettext
from wtforms import TextAreaField, validators


class AdminActionForm(FlaskForm):
    reason = TextAreaField(validators=[
        validators.DataRequired(message=lazy_gettext("You need to specify a reason for taking this action."))
    ])
