from flask_wtf import Form
from wtforms import StringField, validators
from flask.ext.babel import gettext


class ClientForm(Form):
    name = StringField(gettext('Application name'), [
        validators.DataRequired(message=gettext("Application name field is empty.")),
        validators.Length(min=3, message=gettext("Application name needs to be at least 3 characters long.")),
        validators.Length(max=64, message=gettext("Application name needs to be at most 64 characters long."))])
    desc = StringField(gettext('Description'), [
        validators.DataRequired(message=gettext("Client description field is empty.")),
        validators.Length(min=3, message=gettext("Client description needs to be at least 3 characters long.")),
        validators.Length(max=512, message=gettext("Client description needs to be at most 512 characters long."))])
    website = StringField(gettext('Homepage'), [
        validators.DataRequired(message=gettext("Homepage field is empty.")),
        validators.URL(message=gettext("Homepage is not a valid URI."))])
    redirect_uri = StringField(gettext('Authorization callback URL'), [
        validators.DataRequired(message=gettext("Authorization callback URL field is empty.")),
        validators.URL(message=gettext("Authorization callback URL is invalid."))])

