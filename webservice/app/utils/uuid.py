import re

UUID_RE = re.compile(
    r'^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$')
    
def validate(value):
    ''' Validate UUID '''
    try:
        return UUID_RE.match(value)
    except TypeError:
        return False
