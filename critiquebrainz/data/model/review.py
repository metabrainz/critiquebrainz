"""
Review model doesn't contain text of the review, it references revision which
contain different versions of the test.
"""
from critiquebrainz.data import db
from sqlalchemy import desc, func, and_
from sqlalchemy.ext.hybrid import hybrid_property
from sqlalchemy.dialects.postgresql import UUID
from critiquebrainz.data.model.vote import Vote
from critiquebrainz.data.model.revision import Revision
from critiquebrainz.data.model.mixins import DeleteMixin
from critiquebrainz.data.constants import review_classes
from werkzeug.exceptions import BadRequest
from flask_babel import gettext
from datetime import datetime, timedelta
import pycountry

DEFAULT_LICENSE_ID = u"CC BY-SA 3.0"

supported_languages = []
for lang in list(pycountry.languages):
    if 'alpha2' in dir(lang):
        supported_languages.append(lang.alpha2)


class Review(db.Model, DeleteMixin):
    __tablename__ = 'review'

    id = db.Column(UUID, primary_key=True, server_default=db.text('uuid_generate_v4()'))
    release_group = db.Column(UUID, index=True, nullable=False)
    user_id = db.Column(UUID, db.ForeignKey('user.id', ondelete='CASCADE'), nullable=False)
    edits = db.Column(db.Integer, nullable=False, default=0)
    is_archived = db.Column(db.Boolean, nullable=False, default=False)
    is_draft = db.Column(db.Boolean, nullable=False, default=False)
    license_id = db.Column(db.Unicode, db.ForeignKey('license.id', ondelete='CASCADE'), nullable=False)
    language = db.Column(db.String(3), default='en', nullable=False)
    source = db.Column(db.Unicode)
    source_url = db.Column(db.Unicode)

    revisions = db.relationship('Revision', order_by='Revision.timestamp', backref='review',
                                lazy='joined', cascade='delete')

    __table_args__ = (db.UniqueConstraint('release_group', 'user_id'), )

    def to_dict(self):
        response = dict(id=self.id,
                        release_group=self.release_group,
                        user=self.user.to_dict(),
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
        return response

    @property
    def last_revision(self):
        """Returns latest revision of this review."""
        return self.revisions[-1]

    @property
    def text(self):
        """Returns text of the latest revision."""
        return self.last_revision.text  # latest revision

    @hybrid_property
    def created(self):
        """Returns creation time of this review (first revision)."""
        if self.revisions:
            return self.revisions[0].timestamp
        else:
            return None

    @created.expression
    def created(cls):
        return Revision.timestamp

    @property
    def votes_positive_count(self):
        return self.last_revision.votes_positive_count

    @property
    def votes_negative_count(self):
        return self.last_revision.votes_negative_count

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
    def list(cls, release_group=None, user_id=None, sort=None, limit=None,
             offset=None, language=None, license_id=None, inc_drafts=False):
        """Get a list of reviews.

        This method provides several filters that can be used to select
        specific reviews. See argument description below for more info.

        Args:
            release_group: MBID of the release group that is associated with a
                review.
            user_id: UUID of the author.
            sort: Order of returned reviews. Can be either "rating" (order by
                rating), "popularity" (order using recent votes), or "created"
                (order by creation time).
            limit: Maximum number of reviews returned by this method.
            offset: Offset that can be used in conjunction with the limit.
            language: Language (code) of returned reviews.
            licence_id: License of returned reviews.
            inc_drafts: True if reviews marked as drafts should be included,
                False if not.

        Returns:
            List of reviews that match applied filters (if any).
        """
        query = Review.query.filter(Review.is_archived == False)
        if not inc_drafts:
            query = query.filter(Review.is_draft == False)

        # SORTING:

        if sort == 'rating' or sort == 'popularity':
            # Ordering by rating (positive votes - negative votes) and
            # popularity (recent votes).

            # TODO: Simplify this part. It can probably be rewritten using
            # hybrid attributes (by making rating property a hybrid_property),
            # but I'm not sure how to do that.

            # Preparing base query for getting votes
            vote_query_base = db.session.query(
                Vote.revision_id,        # revision associated with a vote
                Vote.vote,               # vote itself (True if positive, False if negative)
                func.count().label('c')  # number of votes
            ).group_by(Vote.revision_id, Vote.vote)

            if sort == 'popularity':
                # When sorting by popularity, we use only votes from the last
                # two weeks to calculate rating.
                vote_query_base = vote_query_base\
                    .filter(Vote.rated_at > datetime.now() - timedelta(weeks=2))

            # Getting positive votes
            votes_pos = vote_query_base.subquery('votes_pos')
            query = query.outerjoin(Revision).outerjoin(
                votes_pos, and_(votes_pos.c.revision_id == Revision.id,
                                votes_pos.c.vote == True))

            # Getting negative votes
            votes_neg = vote_query_base.subquery('votes_neg')
            query = query.outerjoin(Revision).outerjoin(
                votes_neg, and_(votes_neg.c.revision_id == Revision.id,
                                votes_neg.c.vote == False))

            query = query.order_by(desc(func.coalesce(votes_pos.c.c, 0)
                                        - func.coalesce(votes_neg.c.c, 0)))

        elif sort == 'created':  # order by creation time
            query = query.order_by(desc(Review.created)).join(Review.revisions)

        # FILTERING:

        if release_group is not None:
            query = query.filter(Review.release_group == release_group)
        if language is not None:
            query = query.filter(Review.language == language)
        if license_id is not None:
            query = query.filter(Review.license_id == license_id)
        if user_id is not None:
            query = query.filter(Review.user_id == user_id)

        count = query.count()  # Total count should be calculated before limits

        if limit is not None:
            query = query.limit(limit)
        if offset is not None:
            query = query.offset(offset)

        return query.all(), count

    @classmethod
    def create(cls, release_group, user, text, is_draft, license_id=DEFAULT_LICENSE_ID, source=None, source_url=None, language=None):
        review = Review(release_group=release_group, user=user, language=language, is_draft=is_draft,
                        license_id=license_id, source=source, source_url=source_url)
        db.session.add(review)
        db.session.flush()
        db.session.add(Revision(review_id=review.id, text=text))
        db.session.commit()
        return review

    def update(self, text, is_draft=None, license_id=None, language=None):
        """Update contents of this review.

        Returns:
            New revision of this review.
        """
        if license_id is not None:
            if not self.is_draft:  # If trying to convert published review into draft.
                raise BadRequest(gettext("Changing license of a published review is not allowed."))
            self.license_id = license_id

        if language is not None:
            self.language = language

        if is_draft is not None:  # This should be done after all changes that depend on review being a draft.
            if not self.is_draft and is_draft:  # If trying to convert published review into draft.
                raise BadRequest(gettext("Converting published reviews back to drafts is not allowed."))
            self.is_draft = is_draft

        new_revision = Revision(review_id=self.id, text=text)
        db.session.add(new_revision)
        db.session.commit()
        return new_revision
