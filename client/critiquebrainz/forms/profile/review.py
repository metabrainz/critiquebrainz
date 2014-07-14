from flask.ext.wtf import Form, TextAreaField, RadioField, SelectField, BooleanField, validators
from flask.ext.babel import gettext

MIN_REVIEW_LENGTH = 25
MAX_REVIEW_LENGTH = 100000


class ReviewEditForm(Form):
    text = TextAreaField(gettext("Text"), [
        validators.DataRequired(message=gettext("Review is empty!")),
        validators.Length(min=MIN_REVIEW_LENGTH, max=MAX_REVIEW_LENGTH, message=gettext("Review length needs to be between %(min)d and %(max)d characters.", min=MIN_REVIEW_LENGTH, max=MAX_REVIEW_LENGTH))])


class ReviewCreateForm(ReviewEditForm):
    language = SelectField(gettext("Language"), default='en')
    license_choice = RadioField(
        gettext("Licence choice"),
        choices=[
            ('CC BY-SA 3.0', gettext('Allow commercial use of this review (<a href="https://creativecommons.org/licenses/by-sa/3.0/">CC BY-SA 3.0 license</a>)')),
            ('CC BY-NC-SA 3.0', gettext('Do not allow commercial use of this review, unless approved by MetaBrainz Foundation (<a href="https://creativecommons.org/licenses/by-nc-sa/3.0/">CC BY-NC-SA 3.0 license</a>)')),
        ],
        default='CC BY-SA 3.0',
        validators=[validators.DataRequired(message=gettext("You need to choose a license!"))])
    licence = BooleanField(gettext('Licence'), validators=[
        validators.DataRequired(message=gettext("You need to accept the licence agreement!"))])



