from critiquebrainz.data import db


class DeleteMixin(object):
    """Provides a 'delete' method deleting an object from the DB."""
    def delete(self):
        """Delete this object from the DB."""
        db.session.delete(self)
        db.session.flush()
        return self
