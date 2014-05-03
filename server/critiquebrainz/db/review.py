from datetime import datetime

from sqlalchemy.dialects.postgresql import UUID

from . import db
from vote import Vote
from critiquebrainz.constants import review_classes


class Review(db.Model):
    __tablename__ = 'review'

    id = db.Column(UUID, server_default=db.text('uuid_generate_v4()'), primary_key=True)
    release_group = db.Column(UUID, index=True, nullable=False)
    user_id = db.Column(UUID, db.ForeignKey('user.id', ondelete='CASCADE'), nullable=False)
    text = db.Column(db.Unicode, nullable=False)
    created = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    last_updated = db.Column(db.DateTime, onupdate=datetime.utcnow)
    edits = db.Column(db.Integer, nullable=False, default=0)
    is_archived = db.Column(db.Boolean, nullable=False, default=False)

    content_license = db.Column(db.Unicode, nullable=False)
    source = db.Column(db.Unicode)
    source_url = db.Column(db.Unicode)

    spam_reports = db.relationship('SpamReport', cascade='delete', backref='review')
    _votes = db.relationship('Vote', cascade='delete', lazy='dynamic', backref='review')

    __table_args__ = (db.UniqueConstraint('release_group', 'user_id'), )

    # a list of allowed values of `inc` parameter in API calls
    allowed_includes = ('user', )

    def to_dict(self, includes=[]):
        response = dict(id=self.id,
                        release_group=self.release_group,
                        user_id=self.user_id,
                        text=self.text,
                        created=self.created,
                        last_updated=self.last_updated,
                        edits=self.edits,
                        votes_positive=self.votes_positive_count,
                        votes_negative=self.votes_negative_count,
                        rating=self.rating,
                        content_license=self.content_license,
                        source=self.source,
                        source_url=self.source_url,
                        review_class=self.review_class.label)

        if 'user' in includes:
            response['user'] = self.user.to_dict()
        return response

    def delete(self):
        self.is_archived = True
        db.session.commit()
        return self

    @property
    def review_class(self):
        def get_review_class(review):
            for p_class in review_classes:
                if p_class.is_instance(review) is True:
                    return p_class
        if hasattr(self, '_review_class') is False:
            self._review_class = get_review_class(self)
        return self._review_class

    @property
    def votes(self):
        return self._votes.all()

    @property
    def _votes_positive(self):
        return self._votes.filter_by(placet=True)

    @property
    def _votes_negative(self):
        return self._votes.filter_by(placet=False)

    @property
    def votes_positive(self):
        return self._votes_positive.all()

    @property
    def votes_positive_count(self):
        if hasattr(self, '_votes_positive_count') is False:
            self._votes_positive_count = self._votes_positive.count()
        return self._votes_positive_count

    @property
    def votes_negative(self):
        return self._votes_negative.all()

    @property
    def votes_negative_count(self):
        if hasattr(self, '_votes_negative_count') is False:
            self._votes_negative_count = self._votes_negative.count()
        return self._votes_negative_count

    @property
    def rating(self):
        if hasattr(self, '_rating') is False:
            # rating formula (positive votes - negative votes)
            self._rating = self.votes_positive_count - self.votes_negative_count
        return self._rating

    @classmethod
    def list(cls, release_group, user_id, sort, limit, offset):
        # query init
        query = Review.query

        if sort == 'rating':
            # prepare subqueries
            r_q = db.session.query(Vote.review_id, Vote.placet, db.func.count('*').\
                label('c')).group_by(Vote.review_id, Vote.placet)
            r_pos = r_q.subquery('r_pos')
            r_neg = r_q.subquery('r_neg')
            # left join negative votes
            query = query.outerjoin(
                        r_neg,
                        db.and_(
                            r_neg.c.review_id==Review.id,
                            r_neg.c.placet==False))
            # left join positive votes
            query = query.outerjoin(
                        r_pos,
                        db.and_(
                            r_pos.c.review_id==Review.id,
                            r_pos.c.placet==True))
            # order by (positive votes - negative votes) formula
            query = query.order_by(
                        db.desc(
                            (db.func.coalesce(r_pos.c.c, 0) -
                             db.func.coalesce(r_neg.c.c, 0))))
        elif sort == 'created':
            # order by creation date
            query = query.order_by(db.desc(Review.created))
        # filter out archived reviews
        query = query.filter(Review.is_archived==False)
        # filter by release_group
        if release_group is not None:
            query = query.filter(Review.release_group==release_group)
        # filter by user_id
        if user_id is not None:
            query = query.filter(Review.user_id==user_id)
        # count all rows
        count = query.count()
        # set limit
        if limit is not None:
            query = query.limit(limit)
        # set offset
        if offset is not None:
            query = query.offset(offset)
        # execute query
        reviews = query.all()
        return reviews, count

    @classmethod
    def create(cls, release_group, user, text):
        review = Review(release_group=release_group, user=user, text=text)
        db.session.add(review)
        db.session.commit()
        return review

    def update(self, release_group=None, text=None):
        if release_group is not None:
            self.release_group = release_group
        if text is not None:
            self.text = text
        db.session.commit()
