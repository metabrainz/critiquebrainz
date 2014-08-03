from critiquebrainz.ws.testing import WebServiceTestCase
from critiquebrainz.data import db
from critiquebrainz.data.model.user import User
import json


class UserViewsTestCase(WebServiceTestCase):

    def test_user_count(self):
        resp = self.client.get('/ws/1/user/')
        data = json.loads(resp.data)
        assert data['count'] == 0

    def test_user_addition(self):
        user = User(display_name=u'Tester 1', email=u'tester1@tesing.org')
        db.session.add(user)
        db.session.commit()

        resp = self.client.get('/ws/1/user/')
        data = json.loads(resp.data)
        assert data['count'] == 1
