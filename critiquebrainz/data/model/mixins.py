from critiquebrainz.data import db
from flask import current_app
from flask_login import UserMixin, AnonymousUserMixin


class DeleteMixin(object):
    """Provides a 'delete' method deleting an object from the DB."""
    def delete(self):
        """Delete this object from the DB."""
        db.session.delete(self)
        db.session.commit()
        return self


class AdminMixin(UserMixin):
    """Allows a method to check if the current user is admin."""
    def is_admin(self):
        return self.musicbrainz_id in current_app.config['ADMINS']


class AnonymousUser(AnonymousUserMixin):
    def is_admin(self):
        return False
