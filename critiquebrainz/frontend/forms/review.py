from flask_wtf import Form
from flask_babel import lazy_gettext, Locale
from wtforms import TextAreaField, RadioField, SelectField, BooleanField, StringField, validators, IntegerField
from wtforms.validators import ValidationError
from wtforms.widgets import HiddenInput, Input
from babel.core import UnknownLocaleError
from critiquebrainz.db.review import supported_languages
import pycountry

MIN_REVIEW_LENGTH = 25
MAX_REVIEW_LENGTH = 100000


class StateAndLength(validators.Length):
    def __call__(self, form, field):
        if form.state.data == "draft":
            return
        l = len(field.data) if field.data else 0
        if l < self.min or self.max != -1 and l > self.max:
            raise ValidationError(self.message)


# Loading supported languages
languages = []
for language_code in supported_languages:
    try:
        languages.append((language_code, Locale(language_code).language_name))
    except UnknownLocaleError:
        languages.append((language_code, pycountry.languages.get(iso639_1_code=language_code).name))


class ReviewEditForm(Form):
    state = StringField(widget=HiddenInput(), default='draft', validators=[validators.DataRequired()])
    text = TextAreaField(lazy_gettext("Text"), [
        validators.Optional(),
        StateAndLength(min=MIN_REVIEW_LENGTH, max=MAX_REVIEW_LENGTH,
                       message=lazy_gettext("Text length needs to be between %(min)d and %(max)d characters.",
                                            min=MIN_REVIEW_LENGTH, max=MAX_REVIEW_LENGTH))])
    license_choice = RadioField(
        choices=[
            ('CC BY-SA 3.0', lazy_gettext('Allow commercial use of this review(<a href="https://creativecommons.org/licenses/by-sa/3.0/" target="_blank">CC BY-SA 3.0 license</a>)')),  # noqa: E501
            ('CC BY-NC-SA 3.0', lazy_gettext('Do not allow commercial use of this review, unless approved by MetaBrainz Foundation (<a href="https://creativecommons.org/licenses/by-nc-sa/3.0/" target="_blank">CC BY-NC-SA 3.0 license</a>)')),  # noqa: E501
        ],
        validators=[validators.DataRequired(message=lazy_gettext("You need to choose a license!"))])
    language = SelectField(lazy_gettext("You need to accept the license agreement!"), choices=languages)
    rating = IntegerField(lazy_gettext("Rating"), widget=Input(input_type='number'), validators=[validators.Optional()])

    def __init__(self, default_license_id='CC BY-SA 3.0', default_language='en', **kwargs):
        kwargs.setdefault('license_choice', default_license_id)
        kwargs.setdefault('language', default_language)
        Form.__init__(self, **kwargs)

    def validate(self):
        if not super(ReviewEditForm, self).validate():
            return False
        if not self.text.data and not self.rating.data:
            self.text.errors.append("You must provide some text or a rating to complete this review.")
            return False
        return True


class ReviewCreateForm(ReviewEditForm):
    agreement = BooleanField(validators=[
        validators.DataRequired(message=lazy_gettext("You need to accept the license agreement!")),
    ])


class ReviewReportForm(Form):
    reason = TextAreaField(validators=[validators.DataRequired()])
