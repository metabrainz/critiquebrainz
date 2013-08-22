from . import db
from sqlalchemy.dialects.postgresql import UUID
from datetime import datetime

class User(db.Model):

    __tablename__ = 'user'
    
    id = db.Column(UUID, primary_key=True, 
        server_default=db.text("uuid_generate_v4()"))
    display_name = db.Column(db.Unicode, nullable=False)
    email = db.Column(db.Unicode)
    created = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    karma = db.Column(db.Integer, nullable=False, default=0)
    twitter_id = db.Column(db.Unicode, unique=True)
    musicbrainz_id = db.Column(db.Unicode, unique=True)

    publications = db.relationship('Publication', cascade='delete', backref='user')
    rates = db.relationship('Rate', cascade='delete', backref='user')
    spam_reports = db.relationship('SpamReport', cascade='delete', backref='user')
    clients = db.relationship('OAuthClient', cascade='delete', backref='user')
    grants = db.relationship('OAuthGrant', cascade='delete', backref='user')
    tokens = db.relationship('OAuthToken', cascade='delete', backref='user')

    # a list of allowed values of `inc` parameter in API calls
    allowed_includes = ['publications']

    def to_dict(self, includes=[], confidental=False):
        response = dict(id = self.id,
            display_name = self.display_name,
            created = self.created,
            karma = self.karma, )
        if confidental is True:
            response.update(dict(email=self.email, 
                                 twitter_id=self.twitter_id,
                                 musicbrainz_id=self.musicbrainz_id))
        if 'publications' in includes:
            response['publications'] = [p.to_dict() for p in self.publications]
        return response

    def delete(self):
        db.session.delete(self)
        db.session.commit()
        return self

    @classmethod
    def get_or_create(cls, display_name, **kwargs):
        user = cls.query.filter_by(**kwargs).first()

        if user is None:
            user = cls(display_name=display_name,
                **kwargs)
            db.session.add(user)
            db.session.commit()

        return user
        
    # Flask-Login required methods
    def is_authenticated(self):
        return True

    def is_active(self):
        return True

    def is_anonymous(self):
        return False

    def get_id(self):
        return self.id

