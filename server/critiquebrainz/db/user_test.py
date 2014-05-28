from flask.ext.testing import TestCase

from critiquebrainz import create_app
from critiquebrainz.db import db, User, Review, License, Vote
import test_config


class UserTestCase(TestCase):
    def create_app(self):
        return create_app(test_config)

    def setUp(self):
        db.create_all()

    def tearDown(self):
        db.session.remove()
        db.drop_all()

    def test_user_list(self):
        users, count = User.list()
        assert len(users) == 0 and count == 0

        users, count = User.list(0, 0)
        assert len(users) == 0 and count == 0

        users, count = User.list(0, 10)
        assert len(users) == 0 and count == 0

        user_1 = User(display_name=u'Tester #1')
        user_2 = User(display_name=u'Tester #2')
        db.session.add(user_1)
        db.session.add(user_2)
        db.session.commit()

        users, count = User.list()
        assert len(users) == 2 and count == 2

        users, count = User.list(0, 0)
        assert len(users) == 0 and count == 2

        users, count = User.list(1, 1)
        assert len(users) == 1 and count == 2

    def test_user_creation_and_removal(self):
        user_1 = User(display_name=u'Tester #1', email=u'tester@testing.org')
        user_2 = User(display_name=u'Tester #2')
        db.session.add(user_1)
        db.session.add(user_2)
        db.session.commit()

        users, count = User.list()
        assert count == 2

        db.session.delete(user_1)
        db.session.commit()

        users, count = User.list()
        assert count == 1

        stored_user = users[0]
        assert stored_user.id == user_2.id
        assert stored_user.display_name == user_2.display_name
        assert stored_user.email is None

    def test_user_get_or_create(self):
        user_1 = User.get_or_create(u'Tester #1', musicbrainz_id=u'1')
        user_2 = User.get_or_create(u'Tester #2', musicbrainz_id=u'1')
        user_3 = User.get_or_create(u'Tester #3', musicbrainz_id=u'2')

        assert user_1 == user_2
        assert user_1 != user_3

        users, count = User.list()
        assert count == 2

    def test_user_delete(self):
        user = User(display_name=u'Tester')
        db.session.add(user)
        db.session.commit()

        users, count = User.list()
        assert count == 1

        user.delete()
        users, count = User.list()
        assert count == 0

    def test_user_has_voted(self):
        # Review needs user
        user_1 = User(display_name=u'Tester #1')
        db.session.add(user_1)
        db.session.commit()
        # and license
        license = License(id=u"Test", full_name=u'Test License')
        db.session.add(license)
        db.session.commit()
        review = Review.create(user=user_1,
                               release_group='e7aad618-fa86-3983-9e77-405e21796eca',
                               text=u"Testing!",
                               license_id=license.id)
        db.session.add(review)
        db.session.commit()

        user_2 = User(display_name=u'Tester #2')
        db.session.add(user_2)
        db.session.commit()

        assert not user_2.has_voted(review)
        Vote.create(user_2, review, True)
        assert user_2.has_voted(review)
