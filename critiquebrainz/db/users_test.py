from sqlalchemy.exc import DatabaseError
from critiquebrainz.data.testing import DataTestCase
from critiquebrainz.data.model.user import User
from critiquebrainz.db import users
from critiquebrainz.db.users import _avatar
from hashlib import md5


class UserTestCase(DataTestCase):
    def setUp(self):
        super(UserTestCase, self).setUp()
        self.user1 = User.get_or_create("test", musicbrainz_id='0')
        self.user2 = User.get_or_create("test1", musicbrainz_id='1')

    def test_get_many_by_mb_username(self):
        self.users = [self.user1.display_name, self.user2.display_name]
        self.assertEqual(type(users.get_many_by_mb_username(self.users)), list)
        self.assertRaises(DatabaseError, users.get_many_by_mb_username, [])

    def test_avatar(self):
        user3 = {'display_name': 'test2',
                 'id': '3',
                 'email': None,
                 'show_gravatar:': False,
                 }
        gravatar_url = "https://gravatar.com/avatar/{0}{1}"
        test_link = gravatar_url.format(md5(user3['id'].encode('utf-8'))
                                        .hexdigest(), "?d=identicon")
        link = _avatar(user3)
        self.assertEqual(test_link, link)
