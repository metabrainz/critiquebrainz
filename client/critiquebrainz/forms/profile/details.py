from flask.ext.wtf import Form, TextField, BooleanField, validators
from flask.ext.babel import gettext


class EditForm(Form):
    display_name = TextField(gettext('Display name'), [
        validators.DataRequired(message=gettext("Display name field is empty")),
        validators.Length(min=3, message=gettext("Display name needs to be at least 3 characters long.")),
        validators.Length(max=64, message=gettext("Display name needs to be at most 64 characters long."))])
    email = TextField(gettext('Email'), [
        validators.Optional(strip_whitespace=False),
        validators.Email(message=gettext("Email field is not a valid email address"))])
    show_gravatar = BooleanField(gettext('Show my Gravatar'))
