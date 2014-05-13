from datetime import datetime
from sqlalchemy.dialects.postgresql import UUID
from . import db


class Vote(db.Model):
    __tablename__ = 'vote'

    user_id = db.Column(UUID, db.ForeignKey('user.id', ondelete='CASCADE'), primary_key=True)
    review_id = db.Column(UUID, db.ForeignKey('review.id', ondelete='CASCADE'), primary_key=True)
    revision_id = db.Column(db.Integer, db.ForeignKey('revision.id', ondelete='CASCADE'), primary_key=True)
    placet = db.Column(db.Boolean, nullable=False)
    rated_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)

    @classmethod
    def create(cls, user, review, placet):
        # changing votes of an archived review is forbidden
        if review.is_archived is True:
            return
        # delete the vote if it exists
        cls.query.filter_by(user=user, review=review).delete()
        # create a new vote
        last_revision = review.revisions[-1]
        vote = cls(user=user, review=review, revision=last_revision, placet=placet)
        db.session.add(vote)
        db.session.commit()

    def delete(self):
        db.session.delete(self)
        db.session.commit()
        return self

    @classmethod
    def get(cls, user, review):
        vote = cls.query.filter_by(user=user, review=review).first()
        return vote

    def to_dict(self):
        response = dict(placet=self.placet, voted_at=self.rated_at)
        return response
