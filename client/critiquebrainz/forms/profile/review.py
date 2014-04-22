from flask.ext.wtf import Form, TextField, TextAreaField, BooleanField, validators

class CreateForm(Form):
    text = TextAreaField('Text', [
            validators.DataRequired(message="Review field is empty"),
            validators.Length(min=25, message="Review needs to be at least 25 characters long.")])
    licence = BooleanField('Licence', [
            validators.DataRequired(message="You need to accept the licence agreement")])

class EditForm(Form):
    text = TextAreaField('Text', [
            validators.DataRequired(message="Review field is empty"),
            validators.Length(min=25, message="Review needs to be at least 25 characters long.")])
