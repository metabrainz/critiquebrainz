from critiquebrainz.data import db
from sqlalchemy.dialects.postgresql import UUID
from vote import Vote
from revision import Revision
from critiquebrainz.constants import review_classes
import pycountry

DEFAULT_LICENSE_ID = u"CC BY-SA 3.0"
supported_languages = []
for lang in list(pycountry.languages):
    if 'alpha2' in dir(lang):
        supported_languages.append(lang.alpha2)


class Review(db.Model):
    __tablename__ = 'review'

    id = db.Column(UUID, primary_key=True, server_default=db.text('uuid_generate_v4()'))
    release_group = db.Column(UUID, index=True, nullable=False)
    user_id = db.Column(UUID, db.ForeignKey('user.id', ondelete='CASCADE'), nullable=False)
    edits = db.Column(db.Integer, nullable=False, default=0)
    is_archived = db.Column(db.Boolean, nullable=False, default=False)
    license_id = db.Column(db.Unicode, db.ForeignKey('license.id', ondelete='CASCADE'), nullable=False)
    language = db.Column(db.String(3), default='en', nullable=False)
    source = db.Column(db.Unicode)
    source_url = db.Column(db.Unicode)

    votes_positive_count = db.Column(db.Integer, nullable=False, default=0)
    votes_negative_count = db.Column(db.Integer, nullable=False, default=0)

    revisions = db.relationship('Revision', order_by='Revision.timestamp', cascade='delete', backref='review')

    __table_args__ = (db.UniqueConstraint('release_group', 'user_id'), )

    # a list of allowed values of `inc` parameter in API calls
    allowed_includes = ('user', )

    def to_dict(self, includes=[], is_dump=False):
        response = dict(id=self.id,
                        release_group=self.release_group,
                        user=self.user_id,
                        text=self.text,
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
    def first_revision(self):
        """Returns first revision of this review."""
        return self.revisions[0]

    @property
    def last_revision(self):
        """Returns latest revision of this review."""
        return self.revisions[-1]

    @property
    def text(self):
        """Returns text of the latest revision."""
        return self.last_revision.text  # latest revision

    @property
    def created(self):
        """Returns creation time of this review (first revision)."""
        return self.first_revision.timestamp  # first revision

    @property
    def votes_positive(self):
        """Returns positive votes from the latest revision of this review."""
        return self.last_revision.votes_positive

    @property
    def votes_negative(self):
        """Returns negative votes from the latest revision of this review."""
        return self.last_revision.votes_negative

    @property
    def review_class(self):
        """Returns class of this review."""

        def get_review_class(review):
            for c in review_classes:
                if c.is_instance(review) is True:
                    return c

        if hasattr(self, '_review_class') is False:
            self._review_class = get_review_class(self)
        return self._review_class

    @property
    def rating(self):
        if hasattr(self, '_rating') is False:
            self._rating = self.votes_positive_count - self.votes_negative_count
        return self._rating

    @classmethod
    def list(cls, release_group=None, user_id=None, sort=None, limit=None, offset=None, language=None, license_id=None):
        query = Review.query.filter(Review.is_archived == False)

        if sort == 'rating':
            # Descending order of review ratings (votes_positive_count - votes_negative_count).
            query = query.order_by(db.desc(Review.votes_positive_count - Review.votes_negative_count))

        elif sort == 'created':
            rev_q = db.session.query(Revision.review_id, db.func.min(Revision.timestamp).label('creation_time'))\
                .group_by(Revision.review_id).subquery('time')
            query = query.outerjoin(rev_q, Review.id == rev_q.c.review_id)  # left join creation times
            query = query.order_by(db.desc('creation_time'))  # order by creation time

        if release_group is not None:
            query = query.filter(Review.release_group == release_group)
        if language is not None:
            query = query.filter(Review.language == language)
        if license_id is not None:
            query = query.filter(Review.license_id == license_id)
        if user_id is not None:
            query = query.filter(Review.user_id == user_id)
        if limit is not None:
            query = query.limit(limit)
        if offset is not None:
            query = query.offset(offset)
        return query.all(), query.count()

    @classmethod
    def create(cls, release_group, user, text, license_id=DEFAULT_LICENSE_ID, source=None, source_url=None, language=None):
        review = Review(release_group=release_group, user=user, language=language,
                        license_id=license_id, source=source, source_url=source_url)
        db.session.add(review)
        db.session.flush()
        db.session.add(Revision(review_id=review.id, text=text))
        db.session.commit()
        return review

    def update(self, text):
        """Update contents of this review.

        :returns New revision of this review.
        """
        new_revision = Revision(review_id=self.id, text=text)
        db.session.add(new_revision)
        db.session.commit()
        return new_revision

    def update_vote_counts(self):
        query = Vote.query.join(Vote.revision).filter(Revision.review_id == self.id)
        self.votes_positive_count = int(query.filter(Vote.vote == True).count())
        self.votes_negative_count = int(query.filter(Vote.vote == False).count())
        db.session.commit()
