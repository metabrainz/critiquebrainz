from .. import db
from sqlalchemy.dialects.postgresql import UUID
from datetime import datetime


class Vote(db.Model):
    __tablename__ = 'vote'

    user_id = db.Column(UUID, db.ForeignKey('user.id', ondelete='CASCADE'), primary_key=True)
    revision_id = db.Column(db.Integer, db.ForeignKey('revision.id', ondelete='CASCADE'), primary_key=True)
    vote = db.Column(db.Boolean, nullable=False)
    rated_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)

    @classmethod
    def create(cls, user, review, vote):
        # Voting for an archived review is forbidden
        if review.is_archived is True:
            return
        # Deleting the vote from the last revision if it exists
        cls.query.filter_by(user=user, revision=review.last_revision).delete()
        # Creating a new vote for the last revision
        vote = cls(user=user, revision=review.last_revision, vote=vote)
        db.session.add(vote)
        db.session.commit()
        review.update_vote_counts()
        return vote

    def delete(self):
        review = self.revision.review
        db.session.delete(self)
        db.session.commit()
        review.update_vote_counts()
        return self

    def to_dict(self):
        response = dict(vote=self.vote, voted_at=self.rated_at)
        return response
