from critiquebrainz.test_case import ServerTestCase
from critiquebrainz.data import db
from critiquebrainz.data.model.user import User
import json


class UserViewsTestCase(ServerTestCase):

    def test_user_count(self):
        resp = self.client.get('/user/')
        data = json.loads(resp.data)
        assert data['count'] == 0

    def test_user_addition(self):
        user = User(display_name=u'Tester', email=u'tester@tesing.org')
        db.session.add(user)
        db.session.commit()

        resp = self.client.get('/user/')
        data = json.loads(resp.data)
        assert data['count'] == 1
