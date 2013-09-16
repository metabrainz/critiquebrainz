from . import db
from sqlalchemy.dialects.postgresql import UUID
from rate import Rate
from datetime import datetime
from critiquebrainz.constants import publication_classes

class Publication(db.Model):

    __tablename__ = 'publication'

    id = db.Column(UUID, server_default=db.text('uuid_generate_v4()'), primary_key=True)
    release_group = db.Column(UUID, index=True, nullable=False)
    user_id = db.Column(UUID, db.ForeignKey('user.id', ondelete='CASCADE'), nullable=False)
    text = db.Column(db.Unicode, nullable=False)
    created = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    last_updated = db.Column(db.DateTime, onupdate=datetime.utcnow)
    edits = db.Column(db.Integer, nullable=False, default=0)
    is_archived = db.Column(db.Boolean, nullable=False, default=False)

    spam_reports = db.relationship('SpamReport', cascade='delete', backref='publication')
    _rates = db.relationship('Rate', cascade='delete', lazy='dynamic', backref='publication')

    __table_args__ = (db.UniqueConstraint('release_group', 'user_id'), )

    # a list of allowed values of `inc` parameter in API calls
    allowed_includes = ('user', )

    def to_dict(self, includes=[]):
        response = dict(id = self.id,
            release_group = self.release_group,
            user_id = self.user_id,
            text = self.text,
            created = self.created,
            last_updated = self.last_updated,
            edits = self.edits,
            rates_positive = self.rates_positive_count,
            rates_negative = self.rates_negative_count,
            rating = self.rating,
            publication_class = self.publication_class.label)

        if 'user' in includes:
            response['user'] = self.user.to_dict()
        return response

    def delete(self):
        self.is_archived = True
        db.session.commit()
        return self

    @property
    def publication_class(self):
        def get_publication_class(publication):
            for p_class in publication_classes:
                if p_class.is_instance(publication) is True:
                    return p_class
        if hasattr(self, '_publication_class') is False:
            self._publication_class = get_publication_class(self)
        return self._publication_class

    @property
    def rates(self):
        return self._rates.all()

    @property
    def _rates_positive(self):
        return self._rates.filter_by(placet=True)

    @property
    def _rates_negative(self):
        return self._rates.filter_by(placet=False)

    @property
    def rates_positive(self):
        return self._rates_positive.all()

    @property
    def rates_positive_count(self):
        if hasattr(self, '_rates_positive_count') is False:
            self._rates_positive_count = self._rates_positive.count()
        return self._rates_positive_count

    @property
    def rates_negative(self):
        return self._rates_negative.all()

    @property
    def rates_negative_count(self):
        if hasattr(self, '_rates_negative_count') is False:
            self._rates_negative_count = self._rates_negative.count()
        return self._rates_negative_count

    @property
    def rating(self):
        if hasattr(self, '_rating') is False:
            # rating formula (positive rates - negative rates)
            self._rating = self.rates_positive_count - self.rates_negative_count
        return self._rating

    @classmethod
    def list(cls, release_group, user_id, sort, limit, offset):
        # query init
        query = Publication.query

        if sort == 'rating':
            # prepare subqueries
            r_q = db.session.query(Rate.publication_id, Rate.placet, db.func.count('*').\
                label('c')).group_by(Rate.publication_id, Rate.placet)
            r_pos = r_q.subquery('r_pos')
            r_neg = r_q.subquery('r_neg')
            # left join negative rates
            query = query.outerjoin(
                        r_neg,
                        db.and_(
                            r_neg.c.publication_id==Publication.id,
                            r_neg.c.placet==False))
            # left join positive rates
            query = query.outerjoin(
                        r_pos,
                        db.and_(
                            r_pos.c.publication_id==Publication.id,
                            r_pos.c.placet==True))
            # order by (positive rates - negative rates) formula
            query = query.order_by(
                        db.desc(
                            (db.func.coalesce(r_pos.c.c, 0) -
                             db.func.coalesce(r_neg.c.c, 0))))
        elif sort == 'created':
            # order by creation date
            query = query.order_by(db.desc(Publication.created))
        # filter out archived publications
        query = query.filter(Publication.is_archived==False)
        # filter by release_group
        if release_group is not None:
            query = query.filter(Publication.release_group==release_group)
        # filter by user_id
        if user_id is not None:
            query = query.filter(Publication.user_id==user_id)
        # count all rows
        count = query.count()
        # set limit
        if limit is not None:
            query = query.limit(limit)
        # set offset
        if offset is not None:
            query = query.offset(offset)
        # execute query
        publications = query.all()
        return publications, count

    @classmethod
    def create(cls, release_group, user, text):
        publication = Publication(release_group=release_group, user=user, text=text)
        db.session.add(publication)
        db.session.commit()
        return publication

    def update(self, release_group=None, text=None):
        if release_group is not None:
            self.release_group = release_group
        if text is not None:
            self.text = text
        db.session.commit()
