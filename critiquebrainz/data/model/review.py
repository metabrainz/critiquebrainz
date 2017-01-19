"""
Review model doesn't contain text of the review, it references revision which
contain different versions of the test.
"""
from critiquebrainz.data import db
from sqlalchemy import desc, func, and_
from sqlalchemy.orm import aliased
from sqlalchemy.ext.hybrid import hybrid_property
from sqlalchemy.dialects.postgresql import UUID
from critiquebrainz.data.model.vote import Vote
from critiquebrainz.data.model.revision import Revision
from critiquebrainz.data.model.mixins import DeleteMixin
from brainzutils import cache
from werkzeug.exceptions import BadRequest
from flask_babel import lazy_gettext
from datetime import datetime, timedelta
from random import shuffle
import pycountry

DEFAULT_LICENSE_ID = u"CC BY-SA 3.0"

supported_languages = []
for lang in list(pycountry.languages):
    if 'iso639_1_code' in dir(lang):
        supported_languages.append(lang.iso639_1_code)

ENTITY_TYPES = [
    'event',
    'place',
    'release_group',
]


class Review(db.Model, DeleteMixin):
    __tablename__ = 'review'
    CACHE_NAMESPACE = 'Review'

    id = db.Column(UUID, primary_key=True, server_default=db.text('uuid_generate_v4()'))
    entity_id = db.Column(UUID, index=True, nullable=False)
    entity_type = db.Column(db.Enum(*ENTITY_TYPES, name='entity_types'), nullable=False)
    user_id = db.Column(UUID, db.ForeignKey('user.id', ondelete='CASCADE'), nullable=False)
    edits = db.Column(db.Integer, nullable=False, default=0)
    is_draft = db.Column(db.Boolean, nullable=False, default=False)
    is_hidden = db.Column(db.Boolean, nullable=False, default=False)
    license_id = db.Column(db.Unicode, db.ForeignKey('license.id', ondelete='CASCADE'), nullable=False)
    language = db.Column(db.String(3), default='en', nullable=False)
    source = db.Column(db.Unicode)
    source_url = db.Column(db.Unicode)

    revisions = db.relationship('Revision', order_by='Revision.timestamp', backref='review',
                                cascade='delete')

    __table_args__ = (db.UniqueConstraint('entity_id', 'user_id'), )

    def to_dict(self, confidential=False):
        return dict(
            id=self.id,
            entity_id=self.entity_id,
            entity_type=self.entity_type,
            user=self.user.to_dict(confidential=confidential),
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
        )

    @classmethod
    def get(cls, **kwargs):
        return cls.query.filter_by(**kwargs).first()

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
    def rating(self):
        if hasattr(self, '_rating') is False:
            self._rating = self.votes_positive_count - self.votes_negative_count
        return self._rating

    def hide(self):
        self.is_hidden = True
        db.session.commit()

    def unhide(self):
        self.is_hidden = False
        db.session.commit()

    @classmethod
    def list(cls, **kwargs):
        """Get a list of reviews.

        This method provides several filters that can be used to select
        specific reviews. See argument description below for more info.

        Args:
            entity_id: MBID of the entity that is associated with a
                review.
            entity_type: One of the supported reviewable entities. 'release_group'
                or 'event' etc.
            user_id: UUID of the author.
            sort: Order of returned reviews. Can be either "rating" (order by
                rating), or "created" (order by creation time).
            limit: Maximum number of reviews returned by this method.
            offset: Offset that can be used in conjunction with the limit.
            language: Language (code) of returned reviews.
            licence_id: License of returned reviews.
            inc_drafts: True if reviews marked as drafts should be included,
                False if not.
            inc_hidden: True if reviews marked as hidden should be included,
                False if not.

        Returns:
            Pair of values: list of reviews that match applied filters and
            total number of reviews.
        """
        query = Review.query
        inc_drafts = kwargs.pop('inc_drafts', None)
        if not inc_drafts:
            query = query.filter(Review.is_draft == False)

        inc_hidden = kwargs.pop('inc_hidden', None)
        if not inc_hidden:
            query = query.filter(Review.is_hidden == False)

        # FILTERING:

        entity_id = kwargs.pop('entity_id', None)
        if entity_id is not None:
            query = query.filter(Review.entity_id == entity_id)

        entity_type = kwargs.pop('entity_type', None)
        if entity_type is not None:
            query = query.filter(Review.entity_type == entity_type)

        language = kwargs.pop('language', None)
        if language is not None:
            query = query.filter(Review.language == language)

        license_id = kwargs.pop('license_id', None)
        if license_id is not None:
            query = query.filter(Review.license_id == license_id)

        user_id = kwargs.pop('user_id', None)
        if user_id is not None:
            query = query.filter(Review.user_id == user_id)

        count = query.count()  # Total count should be calculated before limits and sorting

        # SORTING:
        sort = kwargs.pop('sort', None)

        if sort == 'rating':  # order by rating (positive votes - negative votes)

            # TODO(roman): Simplify this part. It can probably be rewritten using
            # hybrid attributes (by making rating property a hybrid_property),
            # but I'm not sure how to do that.

            # Preparing base query for getting votes
            vote_query_base = db.session.query(
                Vote.revision_id,        # revision associated with a vote
                Vote.vote,               # vote itself (True if positive, False if negative)
                func.count().label('c')  # number of votes
            ).group_by(Vote.revision_id, Vote.vote)

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
            # Getting publication times for all reviews
            pub_times = db.session.query(
                func.min(Revision.timestamp).label('published_on'),
                Revision.review_id,
            ).group_by(Revision.review_id).subquery('pub_times')

            # Joining and sorting by publication time
            query = query.outerjoin(pub_times).order_by(desc('pub_times.published_on'))

        limit = kwargs.pop('limit', None)
        if limit is not None:
            query = query.limit(limit)

        offset = kwargs.pop('offset', None)
        if offset is not None:
            query = query.offset(offset)

        if kwargs:
            raise TypeError('Unexpected **kwargs: %r' % kwargs)

        return query.all(), count

    @classmethod
    def get_count(cls, **kwargs):
        review_count = 0
        if('is_draft' in kwargs):
            is_drafted = kwargs.pop('is_draft', False)
            review_count += cls.query.filter(cls.is_draft == is_drafted).count()
        if('is_hidden' in kwargs):
            is_hidden = kwargs.pop('is_hidden', False)
            review_count += cls.query.filter(cls.is_hidden == is_hidden).count()
        if(kwargs):
            raise TypeError('Unexpected **kwargs: %r' % kwargs)
        return review_count

    @classmethod
    def create(cls, **kwargs):
        if 'release_group' in kwargs:
            entity_id = kwargs.pop('release_group')
            entity_type = 'release_group'
        else:
            entity_id = kwargs.pop('entity_id')
            entity_type = kwargs.pop('entity_type')

        review = Review(
            entity_id=entity_id,
            entity_type=entity_type,
            user=kwargs.pop('user'),
            language=kwargs.pop('language', None),
            is_draft=kwargs.pop('is_draft', False),
            license_id=kwargs.pop('license_id', DEFAULT_LICENSE_ID),
            source=kwargs.pop('source', None),
            source_url=kwargs.pop('source_url', None)
        )
        db.session.add(review)
        db.session.flush()
        db.session.add(Revision(review_id=review.id, text=kwargs.pop('text')))

        if kwargs:
            db.session.rollback()
            raise TypeError('Unexpected **kwargs: %r' % kwargs)

        db.session.commit()
        cache.invalidate_namespace(Review.CACHE_NAMESPACE)

        return review

    def update(self, **kwargs):
        """Update contents of this review.

        Returns:
            New revision of this review.
        """
        license_id = kwargs.pop('license_id', None)
        if license_id is not None:
            if not self.is_draft:  # If trying to convert published review into draft.
                raise BadRequest(lazy_gettext("Changing license of a published review is not allowed."))
            self.license_id = license_id

        language = kwargs.pop('language', None)
        if language is not None:
            self.language = language

        is_draft = kwargs.pop('is_draft', None)
        if is_draft is not None:  # This should be done after all changes that depend on review being a draft.
            if not self.is_draft and is_draft:  # If trying to convert published review into draft.
                raise BadRequest(lazy_gettext("Converting published reviews back to drafts is not allowed."))
            self.is_draft = is_draft

        new_revision = Revision.create(self.id, kwargs.pop('text'))
        cache.invalidate_namespace(Review.CACHE_NAMESPACE)

        if kwargs:
            # FIXME: Revision creation and other changes need to be rolled back
            # there, but there's a `commit` in Revision.create.
            raise TypeError('Unexpected **kwargs: %r' % kwargs)

        return new_revision

    @classmethod
    def get_popular(cls, limit=None):
        """Get list of popular reviews.

        Popularity is determined by rating of a particular review. Rating is a
        difference between positive votes and negative. In this case only votes
        from the last month are used to calculate rating.

        Results are cached for 12 hours.

        Args:
            limit: Maximum number of reviews to return.

        Returns:
            Randomized list of popular reviews which are converted into
            dictionaries using to_dict method.
        """
        cache_key = cache.gen_key('popular_reviews', limit)
        reviews = cache.get(cache_key, Review.CACHE_NAMESPACE)

        if not reviews:
            # Selecting reviews for distinct release groups
            # TODO(roman): The is a problem with selecting popular reviews like
            # this: if there are multiple reviews for a release group we don't
            # choose the most popular.
            distinct_subquery = db.session.query(Review) \
                .filter(Review.is_draft == False) \
                .distinct(Review.entity_id).subquery()

            # Randomizing results to get some variety
            rand_subquery = db.session.query(aliased(Review, distinct_subquery)) \
                .order_by(func.random()).subquery()

            # Sorting reviews by rating
            query = db.session.query(aliased(Review, rand_subquery))

            # Preparing base query for getting votes
            vote_query_base = db.session.query(
                Vote.revision_id, Vote.vote, func.count().label('c')) \
                .group_by(Vote.revision_id, Vote.vote) \
                .filter(Vote.rated_at > datetime.now() - timedelta(weeks=4))

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

            if limit is not None:
                # Selecting more reviews there so we'll have something
                # different to show (shuffling is done below).
                query = query.limit(limit * 4)

            reviews = query.all()
            reviews = [review.to_dict(confidential=True) for review in reviews]
            cache.set(cache_key, reviews, 1 * 60 * 60, Review.CACHE_NAMESPACE)  # 1 hour

        shuffle(reviews)  # a bit more variety
        return reviews[:limit]
