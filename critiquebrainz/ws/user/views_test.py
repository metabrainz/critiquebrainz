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
        db_users.create(
            display_name='Tester 1',
            email='tester1@tesing.org',
        )
        resp = self.client.get('/user/').json
        self.assertEqual(resp['count'], 1)
        self.assertEqual(len(resp['users']), 1)
        # TODO(roman): Completely verify output (I encountered unicode issues when tried to do that).

    def test_user_entity_handler(self):
        user = User(db_users.create(
            display_name='Tester 1',
            email='tester1@testing.org',
        ))
        resp = self.client.get('/user/{user_id}'.format(user_id=user.id)).json
        self.assertEqual(resp['user']['display_name'], 'Tester 1')
        # Test if user with specified ID does not exist
        self.assert404(self.client.get('/user/e7aad618-fd86-3983-9e77-405e21796eca'))
