from critiquebrainz.data import db
from sqlalchemy.dialects.postgresql import UUID
from critiquebrainz.data.model.mixins import DeleteMixin


class OAuthToken(db.Model, DeleteMixin):
    __tablename__ = 'oauth_token'

    id = db.Column(db.Integer, primary_key=True)
    client_id = db.Column(db.Unicode, db.ForeignKey('oauth_client.client_id', onupdate='CASCADE', ondelete='CASCADE'), nullable=False)
    access_token = db.Column(db.Unicode, unique=True, nullable=False)
    refresh_token = db.Column(db.Unicode, unique=True, nullable=False)
    expires = db.Column(db.DateTime, nullable=False)
    scopes = db.Column(db.UnicodeText)

    # Resource owner
    user_id = db.Column(UUID, db.ForeignKey('user.id', ondelete='CASCADE'), nullable=False)

    def get_scopes(self):
        if hasattr(self, '_scopes') is False:
            if self.scopes:
                self._scopes = self.scopes.split()
            else:
                self._scopes = []
        return self._scopes

    @classmethod
    def purge_tokens(cls, client_id, user_id):
        cls.query.filter_by(client_id=client_id, user_id=user_id).delete()
        db.session.commit()

    def to_dict(self):
        response = dict(refresh_token=self.refresh_token,
                        scopes=self.scopes,
                        client=self.client.to_dict())
        return response
