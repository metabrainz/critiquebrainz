from .. import db
from sqlalchemy.dialects.postgresql import UUID
from critiquebrainz.data.model.vote import Vote
from critiquebrainz.data.model.revision import Revision
from critiquebrainz.constants import review_classes
import pycountry

DEFAULT_LICENSE_ID = u"CC BY-SA 3.0"
supported_languages = []
for lang in list(pycountry.languages):
    if 'alpha2' in dir(lang):
        supported_languages.append(lang.alpha2)


class Review(db.Model):
    __tablename__ = 'review'

    id = db.Column(UUID, server_default=db.text('uuid_generate_v4()'), primary_key=True)
    release_group = db.Column(UUID, index=True, nullable=False)
    user_id = db.Column(UUID, db.ForeignKey('user.id', ondelete='CASCADE'), nullable=False)
    edits = db.Column(db.Integer, nullable=False, default=0)
    is_archived = db.Column(db.Boolean, nullable=False, default=False)
    license_id = db.Column(db.Unicode, db.ForeignKey('license.id', ondelete='CASCADE'), nullable=False)
    language = db.Column(db.String(3), default='en', nullable=False)
    source = db.Column(db.Unicode)
    source_url = db.Column(db.Unicode)

    revisions = db.relationship('Revision', order_by="Revision.timestamp", cascade='delete', backref='review')
    _votes = db.relationship('Vote', cascade='delete', lazy='dynamic', backref='review')

    __table_args__ = (db.UniqueConstraint('release_group', 'user_id'), )

    # a list of allowed values of `inc` parameter in API calls
    allowed_includes = ('user', )

    def to_dict(self, includes=[], is_dump=False):
        response = dict(id=self.id,
                        release_group=self.release_group,
                        user=self.user_id,
                        text=self.revisions[-1].text,  # latest revision
                        created=self.revisions[0].timestamp,
                        last_updated=self.revisions[-1].timestamp,
                        edits=self.edits,
                        votes_positive=self.votes_positive_count,
                        votes_negative=self.votes_negative_count,
                        rating=self.rating,
                        license=self.license.to_dict(),
                        language=self.language,
                        source=self.source,
                        source_url=self.source_url,
                        review_class=self.review_class.label)
        if 'user' in includes:
            response['user'] = self.user.to_dict(include_gravatar=(not is_dump))
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
    def list(cls, release_group=None, user_id=None, sort=None, limit=None, offset=None, language=None, license_id=None):
        # query init
        query = Review.query

        if sort == 'rating':
            # prepare subqueries
            r_q = db.session.query(
                Vote.review_id, Vote.placet, db.func.count('*').label('c')).group_by(Vote.review_id, Vote.placet)
            r_pos = r_q.subquery('r_pos')
            r_neg = r_q.subquery('r_neg')
            # left join negative votes
            query = query.outerjoin(r_neg,
                                    db.and_(r_neg.c.review_id == Review.id,
                                            r_neg.c.placet == False))
            # left join positive votes
            query = query.outerjoin(r_pos,
                                    db.and_(r_pos.c.review_id == Review.id,
                                            r_pos.c.placet == True))
            # order by (positive votes - negative votes) formula
            query = query.order_by(db.desc(db.func.coalesce(r_pos.c.c, 0) - db.func.coalesce(r_neg.c.c, 0)))
        elif sort == 'created':
            rev_q = db.session.query(Revision.review_id, db.func.min(Revision.timestamp).label('creation_time')) \
                .group_by(Revision.review_id).subquery('time')
            # left join creation times
            query = query.outerjoin(rev_q, Review.id == rev_q.c.review_id)
            # order by creation time
            query = query.order_by(db.desc('creation_time'))

        query = query.filter(Review.is_archived == False)
        if release_group is not None:
            query = query.filter(Review.release_group == release_group)
        if language is not None:
            query = query.filter(Review.language == language)
        if license_id is not None:
            query = query.filter(Review.license_id == license_id)
        if user_id is not None:
            query = query.filter(Review.user_id == user_id)

        count = query.count()
        if limit is not None:
            query = query.limit(limit)
        if offset is not None:
            query = query.offset(offset)
        reviews = query.all()
        return reviews, count

    @classmethod
    def create(cls, release_group, user, text, license_id=DEFAULT_LICENSE_ID, source=None, source_url=None, language=None):
        review = Review(release_group=release_group, user=user, language=language,
                        license_id=license_id, source=source, source_url=source_url)
        db.session.add(review)
        db.session.commit()
        # Creating new revision
        db.session.add(Revision(review_id=review.id, text=text))
        db.session.commit()
        return review

    def update(self, release_group=None, text=None, license_id=None, source=None, source_url=None, language=None):
        if release_group is not None:
            self.release_group = release_group
        if text is not None:
            new_revision = Revision(review_id=self.id, text=text)
            db.session.add(new_revision)
            db.session.commit()
        if license_id is not None:
            self.license_id = license_id
        if source is not None:
            self.source = source
        if source_url is not None:
            self.source_url = source_url
        if language is not None:
            self.language = source_url
        db.session.commit()
