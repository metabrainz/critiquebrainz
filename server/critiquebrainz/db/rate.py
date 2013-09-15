from . import db
from sqlalchemy.dialects.postgresql import UUID
from datetime import datetime

class Rate(db.Model):

    __tablename__ = 'rate'
    user_id = db.Column(UUID, db.ForeignKey('user.id', ondelete='CASCADE'), primary_key=True)
    publication_id = db.Column(UUID, db.ForeignKey('publication.id', ondelete='CASCADE'), primary_key=True)
    placet = db.Column(db.Boolean, nullable=False)
    rated_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)

    @classmethod
    def create(cls, user, publication, placet):
        # changing rates of an archived publication is forbidden
        if publication.is_archived is True:
            return
        # delete the existing rate, if exists
        cls.query.filter_by(user=user, publication=publication).delete()
        # create a new rate
        rate = cls(user=user, publication=publication, placet=placet)
        db.session.add(rate)
        db.session.commit()

    def delete(self):
        db.session.delete(self)
        db.session.commit()
        return self

    @classmethod
    def get(cls, user, publication):
        rate = cls.query.filter_by(user=user, publication=publication).first()
        return rate

    def to_dict(self):
        response = dict(placet=self.placet,
            rated_at=self.rated_at)
        return response
