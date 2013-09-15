from flask.ext.wtf import Form, TextField, TextAreaField, BooleanField, validators

class CreateForm(Form):
    release_group = TextField('Release group', [
            validators.DataRequired(message="Release group field is empty"), 
            validators.UUID(message="Release group is not a valid UUID")])
    text = TextAreaField('Text', [
            validators.DataRequired(message="Publication field is empty"), 
            validators.Length(min=25, message="Publication needs to be at least 25 characters long.")])
    licence = BooleanField('Licence', [
            validators.DataRequired(message="You need to accept the licence agreement")])

class EditForm(Form):
    text = TextAreaField('Text', [
            validators.DataRequired(message="Publication field is empty"), 
            validators.Length(min=25, message="Publication needs to be at least 25 characters long.")])
