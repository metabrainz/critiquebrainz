from werkzeug.routing import BaseConverter, ValidationError
import re

uuid_re = re.compile(r'^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$')
    
def validate_uuid(value):
    try:
        return uuid_re.match(value)
    except TypeError:
        return False
        
class UUIDConverter(BaseConverter):
    
    def __init__(self, url_map, strict=True):
        super(UUIDConverter, self).__init__(url_map)
        self.strict = strict
    
    @classmethod
    def _register(cls, app):
        app.url_map.converters['uuid'] = cls
        
    def to_python(self, value):
        if self.strict and not validate_uuid(value):
            raise ValidationError()
        return value

    def to_url(self, value):
        return value