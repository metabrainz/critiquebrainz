from flask_wtf import Form
from flask_babel import lazy_gettext
from wtforms import StringField, BooleanField, validators
from wtforms.fields.html5 import EmailField


class ProfileEditForm(Form):
    display_name = StringField(lazy_gettext("Display name"), [
        validators.DataRequired(message=lazy_gettext("Display name field is empty.")),
        validators.Length(min=3, message=lazy_gettext("Display name needs to be at least 3 characters long.")),
        validators.Length(max=64, message=lazy_gettext("Display name needs to be at most 64 characters long."))])
    email = EmailField(lazy_gettext("Email"), [
        validators.Optional(strip_whitespace=False),
        validators.Email(message=lazy_gettext("Email field is not a valid email address."))])
    show_gravatar = BooleanField(lazy_gettext("Show my Gravatar"))
