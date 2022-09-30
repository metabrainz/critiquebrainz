from unittest import mock

import critiquebrainz.db.users as db_users
from critiquebrainz.db.user import User
from critiquebrainz.frontend.testing import FrontendTestCase


class UserViewsTestCase(FrontendTestCase):

    def setUp(self):
        super(UserViewsTestCase, self).setUp()
        self.user = User(db_users.get_or_create(1, "Tester", new_user_data={
            "display_name": u"Tester",
        }))
        self.hacker = User(db_users.create(musicbrainz_row_id = 2, display_name = u"Hacker"))
        self.admin = User(db_users.get_or_create(3, "Admin", new_user_data={
            "display_name": u"Admin",
        }))

    def test_reviews(self):
        # test reviews for user not in db
        response = self.client.get("/user/{user_id}".format(user_id="random-user-id"))
        self.assert404(response, "Can't find a user with reference: random-user-id")

        # test reviews for user present in db, but not logged in
        response = self.client.get("/user/{user_id}".format(user_id=self.user.id))
        self.assert200(response)
        self.assertIn("Tester", str(response.data))

        # test reviews for user present in db, and logged in
        self.temporary_login(self.user)
        response = self.client.get("/user/{user_id}".format(user_id=self.user.id))
        self.assert200(response)
        self.assertIn("Tester", str(response.data))

        # test reviews for user present in db, but without musicbrainz_id
        response = self.client.get("/user/{user_id}".format(user_id=self.hacker.id))
        self.assert200(response)
        self.assertIn("Hacker", str(response.data))

    def test_info(self):
        # test info for user not in db
        response = self.client.get("/user/{user_id}/info".format(user_id="random-user-id"))
        self.assert404(response, "Can't find a user with reference: random-user-id")

        # test info for user present in db
        response = self.client.get("/user/{user_id}/info".format(user_id=self.user.id))
        self.assert200(response)
        self.assertIn("Tester", str(response.data))

    @mock.patch('critiquebrainz.db.user.User.is_admin')
    def test_block_unblock(self, is_user_admin):
        self.temporary_login(self.admin)

        # test block user when user is not in db
        response = self.client.get("/user/{user_id}/block".format(user_id="random-user-id"))
        self.assert404(response, "Can't find a user with reference: random-user-id")

        # make self.admin a moderator
        is_user_admin.return_value = True

        # admin blocks tester
        response = self.client.post(
            "user/{user_id}/block".format(user_id=self.user.id),
            data=dict(reason="Test blocking user."),
            follow_redirects=True,
        )
        self.assertIn("This user account has been blocked.", str(response.data))
        user = db_users.get_by_id(self.user.id)
        self.assertEqual(user["is_blocked"], True)

        # testing when admin blocks an already blocked user
        response = self.client.post(
            "user/{user_id}/block".format(user_id=self.user.id),
            data=dict(reason="Test blocking already blocker user."),
            follow_redirects=True,
        )
        self.assertIn("This account is already blocked.", str(response.data))

        # test unblock user when user is not in db
        response = self.client.get("/user/{user_id}/unblock".format(user_id="random-user-id"))
        self.assert404(response, "Can't find a user with reference: random-user-id")

        # admin unblocks tester
        response = self.client.post(
            "user/{user_id}/unblock".format(user_id=self.user.id),
            data=dict(reason="Test unblocking user."),
            follow_redirects=True,
        )
        self.assertIn("This user account has been unblocked.", str(response.data))
        user = db_users.get_by_id(self.user.id)
        self.assertEqual(user["is_blocked"], False)

        # testing when admin unblocks a user that is not blocked
        response = self.client.post(
            "user/{user_id}/unblock".format(user_id=self.user.id),
            data=dict(reason="Test unblocking user that is not blocked."),
            follow_redirects=True,
        )
        self.assertIn("This account is not blocked.", str(response.data))
