from . import db
from sqlalchemy.dialects.postgresql import UUID

class User(db.Model):

    __tablename__ = 'user'
    
    id = db.Column(UUID, primary_key=True, 
        server_default=db.text("uuid_generate_v4()"))
    display_name = db.Column(db.Unicode, nullable=False)
    email = db.Column(db.Unicode)
    twitter_id = db.Column(db.Unicode, unique=True)
    musicbrainz_id = db.Column(db.Unicode, unique=True)

    publications = db.relationship('Publication')
    rates = db.relationship('Rate')
    spam_reports = db.relationship('SpamReport')

    def to_dict(self, includes=None):
        response = dict(id = self.id,
        	display_name = self.display_name)
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

