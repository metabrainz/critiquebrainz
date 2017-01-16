from critiquebrainz.data.testing import DataTestCase
from critiquebrainz.data.model.user import User
from critiquebrainz.db.users import avatar, get_many_by_mb_username


class UserTestCase(DataTestCase):
    def setUp(self):
        super(UserTestCase, self).setUp()
        self.user1 = User.get_or_create("test", musicbrainz_id='0')
        self.user2 = User.get_or_create("test1", musicbrainz_id='1')

    def test_get_many_by_mb_username(self):
        users = [self.user1.musicbrainz_id, self.user2.musicbrainz_id]
        dbresults = get_many_by_mb_username(users)
        dbresults = [user['musicbrainz_id'] for user in dbresults]
        self.assertEqual(users, dbresults)
        self.assertEqual(get_many_by_mb_username([]), [])

    def test_avatar(self):
        user = {'display_name': 'test2',
                'id': '3',
                'email': None,
                'show_gravatar:': False,
                }
        gravatar_url = "https://gravatar.com/avatar/eccbc87e4b5ce2fe28308fd9f2a7baf3?d=identicon"
        link = avatar(user)
        self.assertEqual(gravatar_url, link)
