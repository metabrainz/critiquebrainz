from werkzeug.exceptions import InternalServerError


# TODO: Get rid of this class
class APIError(InternalServerError):
    def __init__(self, status=500, desc=None, code=None):
        super(APIError, self).__init__(description=desc)
        self.status = status
        if desc is not None:
            self.desc = desc
        if code is not None:
            self.code = code
