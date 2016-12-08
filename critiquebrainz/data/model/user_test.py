from critiquebrainz.data.testing import DataTestCase
from critiquebrainz.data import db
from critiquebrainz.data.model.user import User
from critiquebrainz.data.model.license import License
from critiquebrainz.data.model.review import Review
from critiquebrainz.data.model.vote import Vote
import hashlib


class UserTestCase(DataTestCase):

    def test_user_list(self):
        users, count = User.list()
        self.assertEqual(len(users), 0)
        self.assertEqual(count, 0)

        users, count = User.list(0, 0)
        self.assertEqual(len(users), 0)
        self.assertEqual(count, 0)

        users, count = User.list(0, 10)
        self.assertEqual(len(users), 0)
        self.assertEqual(count, 0)

        user_1 = User(display_name=u'Tester #1')
        user_2 = User(display_name=u'Tester #2')
        db.session.add(user_1)
        db.session.add(user_2)
        db.session.commit()

        users, count = User.list()
        self.assertEqual(len(users), 2)
        self.assertEqual(count, 2)

        users, count = User.list(0, 0)
        self.assertEqual(len(users), 0)
        self.assertEqual(count, 2)

        users, count = User.list(1, 1)
        self.assertEqual(len(users), 1)
        self.assertEqual(count, 2)

    def test_user_creation_and_removal(self):
        user_1 = User(display_name=u'Tester #1', email=u'tester@testing.org')
        user_2 = User(display_name=u'Tester #2')
        db.session.add(user_1)
        db.session.add(user_2)
        db.session.commit()

        users, count = User.list()
        self.assertEqual(count, 2)

        db.session.delete(user_1)
        db.session.commit()

        users, count = User.list()
        self.assertEqual(count, 1)

        stored_user = users[0]
        self.assertEqual(stored_user.id, user_2.id)
        self.assertEqual(stored_user.display_name, user_2.display_name)
        self.assertIsNone(stored_user.email)

    def test_user_get_or_create(self):
        user_1 = User.get_or_create(u'Tester #1', musicbrainz_id=u'1')
        user_2 = User.get_or_create(u'Tester #2', musicbrainz_id=u'1')
        user_3 = User.get_or_create(u'Tester #3', musicbrainz_id=u'2')

        self.assertEqual(user_1, user_2)
        self.assertNotEqual(user_1, user_3)

        self.assertEqual(User.query.count(), 2)

    def test_user_delete(self):
        user = User(display_name=u'Tester')
        db.session.add(user)
        db.session.commit()
        self.assertEqual(User.query.count(), 1)

        user.delete()
        self.assertEqual(User.query.count(), 0)

    def test_user_update(self):
        user = User(display_name=u'Tester #1')
        db.session.add(user)
        db.session.commit()

        # Checking default state
        retrieved_user = User.query.all()[0]
        self.assertEqual(retrieved_user.display_name, u'Tester #1')
        self.assertIsNone(retrieved_user.email)
        self.assertFalse(retrieved_user.show_gravatar)

        user.update(display_name=u'Tester #2', email=u'tester@testers.org', show_gravatar=True)

        # Checking if contents are updated
        retrieved_user = User.query.all()[0]
        self.assertEqual(retrieved_user.display_name, u'Tester #2')
        self.assertEqual(retrieved_user.email, u'tester@testers.org')
        self.assertTrue(retrieved_user.show_gravatar)

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
                               is_draft=False,
                               license_id=license.id)
        db.session.add(review)
        db.session.commit()

        user_2 = User(display_name=u'Tester #2')
        db.session.add(user_2)
        db.session.commit()

        self.assertFalse(user_2.has_voted(review))
        Vote.create(user_2, review, True)
        self.assertTrue(user_2.has_voted(review))

    def test_reviews_property(self):
        user = User(display_name=u'Tester')
        db.session.add(user)
        db.session.commit()

        self.assertEqual(len(user.reviews), 0)

        license = License(id=u"Test", full_name=u'Test License')
        db.session.add(license)
        db.session.flush()
        review = Review.create(user=user,
                               release_group='e7aad618-fa86-3983-9e77-405e21796eca',
                               text=u"Testing!",
                               is_draft=False,
                               license_id=license.id)
        db.session.add(review)
        db.session.commit()
        self.assertEqual(len(user.reviews), 1)

        review.delete()
        self.assertEqual(len(user.reviews), 0)

    def test_avatar_property(self):
        user = User(display_name=u'Tester', email=u"example@example.org")
        db.session.add(user)
        db.session.commit()

        # By default show_gravatar attribute should be set to False
        self.assertFalse(user.show_gravatar)
        # so avatar property returns generic avatar
        self.assertEqual(user.avatar, "https://gravatar.com/avatar/{}?d=identicon".format(hashlib.md5(user.id.encode('utf-8')).hexdigest()))

        # Let's allow to show avatar of this user.
        user.show_gravatar = True
        db.session.commit()

        self.assertTrue(user.show_gravatar)
        self.assertEqual(user.avatar, "https://gravatar.com/avatar/{}?d=identicon&r=pg".format(hashlib.md5(user.email.encode('utf-8')).hexdigest()))

    def test_votes(self):
        user = User(display_name=u'Tester')
        db.session.add(user)
        db.session.commit()

        self.assertEqual(len(user.votes), 0)

        # TODO(roman): Try to add new votes and see if values change.
