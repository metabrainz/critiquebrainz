from datetime import date, timedelta

from critiquebrainz.data.mixins import AdminMixin
from critiquebrainz.data.user_types import user_types
from critiquebrainz.db import users as db_users


class User(AdminMixin):
    # a list of allowed values of `inc` parameter in API calls
    allowed_includes = ('user_type', 'stats')

    def __init__(self, user):
        self.id = str(user.get('id'))
        self.display_name = user.get('display_name')
        self.email = user.get('email')
        self.created = user.get('created')
        self.musicbrainz_username = user.get('musicbrainz_username')
        self.user_ref = user.get('user_ref')
        self.is_blocked = user.get('is_blocked', False)
        self.license_choice = user.get('license_choice', None)
        self.musicbrainz_row_id = user.get('musicbrainz_row_id', None)
    
    @property
    def is_vote_limit_exceeded(self):
        return self.votes_today_count() >= self.user_type.votes_per_day

    @property
    def is_review_limit_exceeded(self):
        return self.reviews_today_count() >= self.user_type.reviews_per_day

    @property
    def karma(self):
        if hasattr(self, '_karma') is False:
            self._karma = db_users.karma(self.id)
        return self._karma

    @property
    def reviews(self):
        return db_users.reviews(self.id)

    @property
    def votes(self):
        return db_users.get_votes(self.id)

    def votes_since(self, date):
        return db_users.get_votes(self.id, from_date=date)

    def votes_since_count(self, date):
        return len(db_users.get_votes(self.id, from_date=date))

    def votes_today(self):
        return self.votes_since(date.today())

    def votes_today_count(self):
        return self.votes_since_count(date.today())

    def reviews_since(self, date):
        return db_users.get_reviews(self.id, from_date=date)

    def reviews_since_count(self, date):
        return len(db_users.get_reviews(self.id, from_date=date))

    def reviews_today(self):
        return self.reviews_since(date.today())

    def reviews_today_count(self):
        return self.reviews_since_count(date.today())

    def comments_since(self, date):
        return db_users.get_comments(self.id, from_date=date)

    def comments_since_count(self, date):
        return len(db_users.get_comments(self.id, from_date=date))

    def comments_today(self):
        return self.comments_since(date.today())

    def comments_today_count(self):
        return self.comments_since_count(date.today())

    @property
    def user_type(self):
        def get_user_type(user):
            for user_type in user_types:
                if user_type.is_instance(user):
                    return user_type

        if hasattr(self, '_user_type') is False:
            self._user_type = get_user_type(self)
        return self._user_type

    @property
    def stats(self):
        today = date.today()
        return dict(
            reviews_today=self.reviews_today_count(),
            reviews_last_7_days=self.reviews_since_count(today - timedelta(days=7)),
            reviews_this_month=self.reviews_since_count(date(today.year, today.month, 1)),
            votes_today=self.votes_today_count(),
            votes_last_7_days=self.votes_since_count(today - timedelta(days=7)),
            votes_this_month=self.votes_since_count(date(today.year, today.month, 1)),
            comments_today=self.comments_today_count(),
            comments_last_7_days=self.comments_since_count(today - timedelta(days=7)),
            comments_this_month=self.comments_since_count(date(today.year, today.month, 1)),
        )

    def to_dict(self, includes=None, confidential=False):
        if includes is None:
            includes = []
        response = dict(
            id=self.id,
            display_name=self.display_name,
            created=self.created,
            karma=self.karma,
            user_type=self.user_type.label,
            musicbrainz_username=self.musicbrainz_username,
            user_ref=self.user_ref,
        )

        if confidential is True:
            response.update(dict(
                email=self.email,
                license_choice=self.license_choice,
            ))

        if 'user_type' in includes:
            response['user_type'] = dict(
                label=self.user_type.label,
                reviews_per_day=self.user_type.reviews_per_day,
                votes_per_day=self.user_type.votes_per_day,
            )

        if 'stats' in includes:
            today = date.today()
            response['stats'] = dict(
                reviews_today=self.reviews_today_count(),
                reviews_last_7_days=self.reviews_since_count(today - timedelta(days=7)),
                reviews_this_month=self.reviews_since_count(date(today.year, today.month, 1)),
                votes_today=self.votes_today_count(),
                votes_last_7_days=self.votes_since_count(today - timedelta(days=7)),
                votes_this_month=self.votes_since_count(date(today.year, today.month, 1)),
                comments_today=self.comments_today_count(),
                comments_last_7_days=self.comments_since_count(today - timedelta(days=7)),
                comments_this_month=self.comments_since_count(date(today.year, today.month, 1)),
            )

        return response
