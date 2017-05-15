from critiquebrainz.ws.testing import WebServiceTestCase
from critiquebrainz.db import users as db_users
from critiquebrainz.db.user import User


class UserViewsTestCase(WebServiceTestCase):
    def test_user_count(self):
        resp = self.client.get('/user/')
        self.assertDictEqual(resp.json, dict(
            count=0,
            limit=50,
            offset=0,
            users=[],
        ))

    def test_user_addition(self):
        user = User(db_users.create(
            display_name='Tester 1',
            email='tester1@tesing.org',
        ))
        resp = self.client.get('/user/').json
        self.assertEqual(resp['count'], 1)
        self.assertEqual(len(resp['users']), 1)
        # TODO(roman): Completely verify output (I encountered unicode issues when tried to do that).
