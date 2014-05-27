import json

from flask.ext.testing import TestCase

from critiquebrainz import create_app
from critiquebrainz.db import db, User
import test_config


class UserTestCase(TestCase):
    def create_app(self):
        return create_app(test_config)

    def setUp(self):
        db.create_all()

    def tearDown(self):
        db.session.remove()
        db.drop_all()

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
