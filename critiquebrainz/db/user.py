from critiquebrainz.data.model.mixins import DeleteMixin, AdminMixin
import critiquebrainz.db.users as db_users
import hashlib
from critiquebrainz.data.constants import user_types
from datetime import date, datetime, timedelta


class User(AdminMixin, DeleteMixin):

    def __init__(self, user):
        self.id = str(user.get('id'))
        self.display_name = user.get('display_name')
        self.email = user.get('email')
        self.created = user.get('created')
        self.musicbrainz_id = user.get('musicbrainz_id')
        self.show_gravatar = user.get('show_gravatar', False)
        self.is_blocked = user.get('is_blocked', False)
        allowed_includes = ('user_type', 'stats')

    @property
    def avatar(self):
        """Link to user's avatar image."""
        if self.show_gravatar and self.email:
            return "https://gravatar.com/avatar/" + hashlib.md5(self.mail.encode("utf-8")).hexdigest() + "?d=identicon&r=pg"
        else:
            return "https://gravatar.com/avatar/" + hashlib.md5(self.id.encode("utf-8")).hexdigest() + "?d=identicon"

    @property
    def is_vote_limit_exceeded(self):
        if self.votes_today_count() >= self.user_type.votes_per_day:
            return True
        else:
            return False

    @property
    def is_review_limit_exceeded(self):
        if self.reviews_today_count() >= self.user_type.reviews_per_day:
            return True
        else:
            return False

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
        return db_users.get_votes(self.id, date=date)

    def votes_since_count(self, date):
        return len(db_users.get_votes(self.id, date=date))

    def votes_today(self):
        return db_users.get_votes(self.id, date.today())

    def votes_today_count(self):
        return len(db_users.get_votes(self.id, date.today()))

    def reviews_since(self, date):
        return db_users.get_reviews(self.id)

    def reviews_since_count(self, date):
        return len(db_users.get_reviews(self.id))

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
            votes_last_7_days=self.votes_since_count(today-timedelta(days=7)),
            votes_this_month=self.votes_since_count(date(today.year, today.month, 1)))

    def to_dict(self, includes=None, confidential=False):
        if includes is None:
            includes = []
        response = dict(id=self.id,
                        display_name=self.display_name,
                        created=self.created,
                        karma=self.karma,
                        user_type=self.user_type.label)

        if confidential is True:
            response.update(dict(email=self.email,
                                 avatar=self.avatar,
                                 show_gravatar=self.show_gravatar,
                                 musicbrainz_id=self.musicbrainz_id))

        if 'user_type' in includes:
            response['user_type'] = dict(
                label=self.user_type.label,
                reviews_per_day=self.user_type.reviews_per_day,
                votes_per_day=self.user_type.votes_per_day)

        if 'stats' in includes:
            today = date.today()
            response['stats'] = dict(
                reviews_today=self.reviews_today_count(),
                reviews_last_7_days=self.reviews_since_count(today - timedelta(days=7)),
                reviews_this_month=self.reviews_since_count(date(today.year, today.month, 1)),
                votes_today=self.votes_today_count(),
                votes_last_7_days=self.votes_since_count(today - timedelta(days=7)),
                votes_this_month=self.votes_since_count(date(today.year, today.month, 1)))

        return response
