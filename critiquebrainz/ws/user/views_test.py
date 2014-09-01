from critiquebrainz.ws.testing import WebServiceTestCase
from critiquebrainz.data import db
from critiquebrainz.data.model.user import User


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
        user = User(display_name=u'Tester 1', email=u'tester1@tesing.org')
        db.session.add(user)
        db.session.commit()
        resp = self.client.get('/user/')
        decoded = resp.json
        self.assertEquals(decoded['count'], 1)
        self.assertEquals(len(decoded['users']), 1)
        # TODO: Completely verify output (I encountered unicode issues when tried to do that).
