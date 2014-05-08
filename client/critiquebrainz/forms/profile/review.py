from flask.ext.wtf import Form, TextAreaField, RadioField, BooleanField, validators


class CreateForm(Form):
    text = TextAreaField('Text', validators=[
        validators.DataRequired(message="Review is empty"),
        validators.Length(min=25, message="Review needs to be at least 25 characters long")])
    license_choice = RadioField(
        'Licence choice',
        choices=[
            ('CC BY-SA 3.0', 'Allow commercial use of this review (<a href="https://creativecommons.org/licenses/by-sa/3.0/">CC BY-SA 3.0 license</a>)'),
            ('CC BY-NC-SA 3.0', 'Do not allow commercial use of this review, unless approved by MetaBrainz Foundation (<a href="https://creativecommons.org/licenses/by-nc-sa/3.0/">CC BY-NC-SA 3.0 license</a>)'),
        ],
        validators=[validators.DataRequired(message="You need to choose license")])
    licence = BooleanField('Licence', validators=[
        validators.DataRequired(message="You need to accept the licence agreement")])


class EditForm(Form):
    text = TextAreaField('Text', [
        validators.DataRequired(message="Review is empty"),
        validators.Length(min=25, message="Review needs to be at least 25 characters long")])
