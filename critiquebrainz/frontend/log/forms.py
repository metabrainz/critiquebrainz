from flask_wtf import Form
from flask_babel import lazy_gettext
from wtforms import TextAreaField, validators


class AdminActionForm(Form):
    reason = TextAreaField(validators=[
        validators.DataRequired(message=lazy_gettext("You need to specify a reason for taking this action."))
    ])
