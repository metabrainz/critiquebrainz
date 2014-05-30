from flask.ext.wtf import Form, TextField, validators
from flask.ext.babel import gettext


class ClientForm(Form):
    name = TextField(gettext('Client name'), [
        validators.DataRequired(message=gettext("Client name field is empty")),
        validators.Length(min=3, message=gettext("Client name needs to be at least 3 characters long.")),
        validators.Length(max=64, message=gettext("Client name needs to be at most 64 characters long."))])
    desc = TextField(gettext('Client description'), [
        validators.DataRequired(message=gettext("Client description field is empty")),
        validators.Length(min=3, message=gettext("Client description needs to be at least 3 characters long.")),
        validators.Length(max=512, message=gettext("Client description needs to be at most 512 characters long."))])
    website = TextField(gettext('Client website'), [
        validators.DataRequired(message=gettext("Client website field is empty")),
        validators.URL(message=gettext("Client website is not a valid URI"))])
    redirect_uri = TextField(gettext('Redirect URI'), [
        validators.DataRequired(message=gettext("Redirect URI field is empty")),
        validators.URL(message=gettext("Redirect URI is not a valid URI"))])

