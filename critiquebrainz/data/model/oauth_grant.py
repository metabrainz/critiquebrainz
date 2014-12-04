from critiquebrainz.data import db
from sqlalchemy.dialects.postgresql import UUID


class OAuthGrant(db.Model):
    __tablename__ = 'oauth_grant'

    id = db.Column(db.Integer, primary_key=True)
    client_id = db.Column(db.Unicode, db.ForeignKey('oauth_client.client_id', onupdate='CASCADE', ondelete='CASCADE'), nullable=False)
    code = db.Column(db.Unicode, index=True, nullable=False)
    expires = db.Column(db.DateTime, nullable=False)
    redirect_uri = db.Column(db.UnicodeText, nullable=False)
    scopes = db.Column(db.UnicodeText)

    # Resource owner
    user_id = db.Column(UUID, db.ForeignKey('user.id', ondelete='CASCADE'), nullable=False)

    def get_scopes(self):
        if hasattr(self, '_scopes') is False:
            self._scopes = self.scopes.split()
        return self._scopes

    def delete(self):
        db.session.delete(self)
        db.session.commit()
        return self
