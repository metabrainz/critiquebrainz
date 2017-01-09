from sqlalchemy.exc import DatabaseError
from critiquebrainz.data.testing import DataTestCase
from critiquebrainz.data.model.user import User
from critiquebrainz.db import users


class UserTestCase(DataTestCase):
    def setUp(self):
        super(UserTestCase, self).setUp()
        self.user1 = User.get_or_create("test", musicbrainz_id='0')
        self.user2 = User.get_or_create("test1", musicbrainz_id='1')
        self.admins = [self.user1.display_name, self.user2.display_name]

    def test_response_type(self):
        self.assertEqual(type(users.get_many_by_mb_username(self.admins)), list)

    def test_exception(self):
        self.assertRaises(DatabaseError, users.get_many_by_mb_username, [])
