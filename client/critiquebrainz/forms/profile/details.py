from flask.ext.wtf import Form, TextField, BooleanField, validators


class EditForm(Form):
    display_name = TextField('Display name', [
        validators.DataRequired(message="Display name field is empty"),
        validators.Length(min=3, message="Display name needs to be at least 3 characters long."),
        validators.Length(max=64, message="Display name needs to be at most 64 characters long.")])
    email = TextField('Email', [
        validators.Optional(),
        validators.Email(message="Email field is not a valid email address")])
    show_gravatar = BooleanField('Show my Gravatar')
