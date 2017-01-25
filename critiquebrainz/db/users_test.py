from critiquebrainz.data.testing import DataTestCase
from critiquebrainz.data.model.user import User
from critiquebrainz.db.users import gravatar_url, get_many_by_mb_username


class UserTestCase(DataTestCase):
    def setUp(self):
        super(UserTestCase, self).setUp()
        self.user1 = User.get_or_create("test", musicbrainz_id='tester_1')
        self.user2 = User.get_or_create("test1", musicbrainz_id="тестер")

    def test_get_many_by_mb_username(self):
        users = [self.user1.musicbrainz_id, self.user2.musicbrainz_id]
        dbresults = get_many_by_mb_username(users)
        dbresults = [user["musicbrainz_id"] for user in dbresults]
        self.assertEqual(users, dbresults)
        self.assertEqual(get_many_by_mb_username([]), [])

    def test_avatar(self):
        self.assertEqual(
            gravatar_url("test2"),
            "https://gravatar.com/avatar/ad0234829205b9033196ba818f7a872b?d=identicon&r=pg"
        )
