from critiquebrainz.exceptions import CritiqueBrainzError


class NotFound(CritiqueBrainzError):
    def __init__(self, desc=None):
        super(NotFound, self).__init__()
        self.status = 404
        self.desc = desc
