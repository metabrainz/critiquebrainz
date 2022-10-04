from flask_wtf import FlaskForm
from flask_babel import lazy_gettext
from wtforms import StringField, BooleanField, RadioField, validators
from wtforms.fields import EmailField


class ProfileEditForm(FlaskForm):
    display_name = StringField(lazy_gettext("Display name"), [
        validators.InputRequired(message=lazy_gettext("Display name field is empty.")),
        validators.Length(min=3, message=lazy_gettext("Display name needs to be at least 3 characters long.")),
        validators.Length(max=64, message=lazy_gettext("Display name needs to be at most 64 characters long."))])
    email = EmailField(lazy_gettext("Email"), [
        validators.Optional(strip_whitespace=False),
        validators.Email(message=lazy_gettext("Email field is not a valid email address."))])
    license_choice = RadioField(lazy_gettext("Preferred License Choice"), choices=[
        ('CC BY-SA 3.0', lazy_gettext('Allow commercial use of my reviews (<a href="https://creativecommons.org/licenses/by-sa/3.0/" target="_blank">CC BY-SA 3.0 license</a>)')),  # noqa: E501
        ('CC BY-NC-SA 3.0', lazy_gettext('Do not allow commercial use of my reviews, unless approved by MetaBrainz Foundation (<a href="https://creativecommons.org/licenses/by-nc-sa/3.0/" target="_blank">CC BY-NC-SA 3.0 license</a>)')),  # noqa: E501
    ])
