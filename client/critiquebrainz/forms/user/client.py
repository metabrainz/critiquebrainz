from flask.ext.wtf import Form, TextField, TextAreaField, BooleanField, validators

class ClientForm(Form):
    name = TextField('Client name', [
            validators.DataRequired(message="Client name field is empty"), 
            validators.Length(min=3, message="Client name needs to be at least 3 characters long."),
            validators.Length(max=64, message="Client name needs to be at most 64 characters long.")])
    desc = TextField('Client description', [
            validators.DataRequired(message="Client description field is empty"), 
            validators.Length(min=3, message="Client description needs to be at least 3 characters long."),
            validators.Length(max=512, message="Client description needs to be at most 512 characters long.")])
    website = TextField('Client website', [
            validators.DataRequired(message="Client website field is empty"), 
            validators.URL(message="Client website is not a valid URI")])
    redirect_uri = TextField('Redirect URI', [
            validators.DataRequired(message="Redirect URI field is empty"), 
            validators.URL(message="Redirect URI is not a valid URI")])

