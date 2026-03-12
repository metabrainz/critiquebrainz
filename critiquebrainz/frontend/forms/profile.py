from flask_wtf import FlaskForm
from flask_babel import lazy_gettext
from wtforms import StringField, validators
from wtforms.fields import EmailField


class ProfileEditForm(FlaskForm):
    display_name = StringField(lazy_gettext("Display name"), [
        validators.InputRequired(message=lazy_gettext("Display name field is empty.")),
        validators.Length(min=3, message=lazy_gettext("Display name needs to be at least 3 characters long.")),
        validators.Length(max=64, message=lazy_gettext("Display name needs to be at most 64 characters long."))])
    email = EmailField(lazy_gettext("Email"), [
        validators.Optional(strip_whitespace=False),
        validators.Email(message=lazy_gettext("Email field is not a valid email address."))])
