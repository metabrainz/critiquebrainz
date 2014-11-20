from critiquebrainz.frontend.exceptions import FrontendError


class APIError(FrontendError):
    def __init__(self, status=500, desc=None, code=None):
        super(APIError, self).__init__()
        self.status = status
        if desc is not None:
            self.desc = desc
        if code is not None:
            self.code = code
