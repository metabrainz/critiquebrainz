from flask_wtf import FlaskForm
from flask_babel import lazy_gettext
from wtforms import TextAreaField, RadioField, SelectField, BooleanField, StringField, validators, IntegerField
from wtforms.validators import ValidationError
from wtforms.widgets import HiddenInput, Input
from critiquebrainz.db.review import supported_languages
from critiquebrainz.frontend.forms.utils import get_language_name

MIN_REVIEW_LENGTH = 25
MAX_REVIEW_LENGTH = 100000


class StateAndLength(validators.Length):
    def __call__(self, form, field):
        if form.state.data == "draft":
            return
        length = len(field.data) if field.data else 0
        if length < self.min or self.max != -1 and length > self.max:
            raise ValidationError(self.message)


# Loading supported languages
languages = []
for language_code in supported_languages:
    languages.append((language_code, get_language_name(language_code)))


class ReviewEditForm(FlaskForm):
    state = StringField(widget=HiddenInput(), default='draft', validators=[validators.InputRequired()])
    text = TextAreaField(lazy_gettext("Text"), [
        validators.Optional(),
        StateAndLength(min=MIN_REVIEW_LENGTH, max=MAX_REVIEW_LENGTH,
                       message=lazy_gettext("Text length needs to be between %(min)d and %(max)d characters.",
                                            min=MIN_REVIEW_LENGTH, max=MAX_REVIEW_LENGTH))])
    remember_license = BooleanField(lazy_gettext("Remember this license choice for further preference"))
    language = SelectField(lazy_gettext("You need to accept the license agreement!"), choices=languages)
    rating = IntegerField(lazy_gettext("Rating"), widget=Input(input_type='number'), validators=[validators.Optional()])

    def __init__(self, default_language='en', **kwargs):
        kwargs.setdefault('language', default_language)
        FlaskForm.__init__(self, **kwargs)

    def validate(self, extra_validators=None):
        if not super(ReviewEditForm, self).validate(extra_validators):
            return False
        if not self.text.data and not self.rating.data:
            self.text.errors.append("You must provide some text or a rating to complete this review.")
            return False
        return True


class ReviewCreateForm(ReviewEditForm):
    agreement = BooleanField(validators=[
        validators.InputRequired(message=lazy_gettext("You need to accept the license agreement!")),
    ])


class ReviewReportForm(FlaskForm):
    reason = TextAreaField(validators=[validators.InputRequired()])
