from flask.ext.wtf import Form, TextAreaField, RadioField, BooleanField, validators
from flask.ext.babel import gettext


class CreateForm(Form):
    text = TextAreaField(gettext('Text'), validators=[
        validators.DataRequired(message=gettext("Review is empty")),
        validators.Length(min=25, message=gettext("Review needs to be at least 25 characters long"))])
    license_choice = RadioField(
        gettext('Licence choice'),
        choices=[
            ('CC BY-SA 3.0', gettext('Allow commercial use of this review (<a href="https://creativecommons.org/licenses/by-sa/3.0/">CC BY-SA 3.0 license</a>)')),
            ('CC BY-NC-SA 3.0', gettext('Do not allow commercial use of this review, unless approved by MetaBrainz Foundation (<a href="https://creativecommons.org/licenses/by-nc-sa/3.0/">CC BY-NC-SA 3.0 license</a>)')),
        ],
        validators=[validators.DataRequired(message=gettext("You need to choose a license"))])
    licence = BooleanField(gettext('Licence'), validators=[
        validators.DataRequired(message=gettext("You need to accept the licence agreement"))])


class EditForm(Form):
    text = TextAreaField(gettext('Text'), [
        validators.DataRequired(message=gettext("Review is empty")),
        validators.Length(min=25, message=gettext("Review needs to be at least 25 characters long"))])
