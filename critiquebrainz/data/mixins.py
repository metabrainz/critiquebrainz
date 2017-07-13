from flask import current_app
from flask_login import UserMixin, AnonymousUserMixin


class AdminMixin(UserMixin):
    """Allows a method to check if the current user is admin."""
    def is_admin(self):
        return self.musicbrainz_username in current_app.config['ADMINS']


class AnonymousUser(AnonymousUserMixin):

    @staticmethod
    def is_admin():
        return False
