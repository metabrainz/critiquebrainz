from datetime import date, timedelta
from critiquebrainz.data.mixins import AdminMixin
from critiquebrainz.db import users as db_users
from critiquebrainz.data.user_types import user_types


class User(AdminMixin):

    # a list of allowed values of `inc` parameter in API calls
    allowed_includes = ('user_type', 'stats')

    def __init__(self, user):
        self.id = str(user.get('id'))
        self.display_name = user.get('display_name')
        self.email = user.get('email')
        self.created = user.get('created')
        self.musicbrainz_username = user.get('musicbrainz_username')
        self.show_gravatar = user.get('show_gravatar', False)
        self.is_blocked = user.get('is_blocked', False)

    @property
    def avatar(self):
        """Link to user's avatar image."""
        if self.show_gravatar and self.email:
            return db_users.gravatar_url(self.email)
        return db_users.gravatar_url(self.id)

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
        )

        if confidential is True:
            response.update(dict(
                email=self.email,
                avatar=self.avatar,
                show_gravatar=self.show_gravatar,
                musicbrainz_username=self.musicbrainz_username,
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
            )

        return response
