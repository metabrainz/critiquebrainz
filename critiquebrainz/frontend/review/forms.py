from flask_wtf import Form
from flask_babel import gettext, Locale
from wtforms import TextAreaField, RadioField, SelectField, BooleanField, StringField, validators
from wtforms.validators import ValidationError
from wtforms.widgets import HiddenInput
from babel.core import UnknownLocaleError
from critiquebrainz.data.model.review import supported_languages
import pycountry

MIN_REVIEW_LENGTH = 25
MAX_REVIEW_LENGTH = 100000


class StateAndLength(validators.Length):
    def __call__(self, form, field):
        if form.state.data == "draft":
            return
        l = field.data and len(field.data) or 0
        if l < self.min or self.max != -1 and l > self.max:
            raise ValidationError(self.message)


# Loading supported languages
languages = []
for language_code in supported_languages:
    try:
        languages.append((language_code, Locale(language_code).language_name))
    except UnknownLocaleError:
        languages.append((language_code, pycountry.languages.get(alpha2=language_code).name))


class ReviewEditForm(Form):
    state = StringField(widget=HiddenInput(), default='draft', validators=[validators.DataRequired()])
    text = TextAreaField(gettext("Text"), [
        validators.DataRequired(message=gettext("Review is empty!")),
        StateAndLength(min=MIN_REVIEW_LENGTH, max=MAX_REVIEW_LENGTH,
                       message=gettext("Review length needs to be between %(min)d and %(max)d characters.",
                                       min=MIN_REVIEW_LENGTH, max=MAX_REVIEW_LENGTH))])
    license_choice = RadioField(
        choices=[
            ('CC BY-SA 3.0', gettext('Allow commercial use of this review (<a href="https://creativecommons.org/licenses/by-sa/3.0/" target="_blank">CC BY-SA 3.0 license</a>)')),
            ('CC BY-NC-SA 3.0', gettext('Do not allow commercial use of this review, unless approved by MetaBrainz Foundation (<a href="https://creativecommons.org/licenses/by-nc-sa/3.0/" target="_blank">CC BY-NC-SA 3.0 license</a>)')),
        ],
        validators=[validators.DataRequired(message=gettext("You need to choose a license!"))])
    language = SelectField(gettext("Language"), choices=languages)

    def __init__(self, default_license_id='CC BY-SA 3.0', default_language='en', **kwargs):
       kwargs.setdefault('license_choice', default_license_id)
       kwargs.setdefault('language', default_language)
       Form.__init__(self, **kwargs)


class ReviewCreateForm(ReviewEditForm):
    agreement = BooleanField(validators=[validators.DataRequired(message=gettext("You need to accept the license agreement!"))])
