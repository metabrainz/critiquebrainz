from werkzeug.routing import BaseConverter, ValidationError
from uuid import validate

class UUIDConverter(BaseConverter):
    
    def __init__(self, url_map, strict=True):
        super(UUIDConverter, self).__init__(url_map)
        self.strict = strict
    
    def to_python(self, value):
        if self.strict and not validate(value):
            raise ValidationError()
        return value

    def to_url(self, value):
        return value

class FlaskUUID(object):

    def __init__(self, app=None):
        if app is not None:
            self.init_app(app)

    def init_app(self, app):
        app.url_map.converters['uuid'] = UUIDConverter
