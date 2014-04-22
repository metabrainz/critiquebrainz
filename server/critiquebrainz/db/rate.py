from . import db
from sqlalchemy.dialects.postgresql import UUID
from datetime import datetime

class Rate(db.Model):

    __tablename__ = 'rate'
    user_id = db.Column(UUID, db.ForeignKey('user.id', ondelete='CASCADE'), primary_key=True)
    review_id = db.Column(UUID, db.ForeignKey('review.id', ondelete='CASCADE'), primary_key=True)
    placet = db.Column(db.Boolean, nullable=False)
    rated_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)

    @classmethod
    def create(cls, user, review, placet):
        # changing rates of an archived review is forbidden
        if review.is_archived is True:
            return
        # delete the existing rate, if exists
        cls.query.filter_by(user=user, review=review).delete()
        # create a new rate
        rate = cls(user=user, review=review, placet=placet)
        db.session.add(rate)
        db.session.commit()

    def delete(self):
        db.session.delete(self)
        db.session.commit()
        return self

    @classmethod
    def get(cls, user, review):
        rate = cls.query.filter_by(user=user, review=review).first()
        return rate

    def to_dict(self):
        response = dict(placet=self.placet,
            rated_at=self.rated_at)
        return response
