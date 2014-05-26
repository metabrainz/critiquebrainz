import unittest
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

    def test_user_creation_and_removal(self):
        user_1 = User(display_name=u'Tester #1', email=u'tester@tesing.org')
        user_2 = User(display_name=u'Tester #2')
        db.session.add(user_1)
        db.session.add(user_2)
        db.session.commit()

        resp = self.client.get('/user/')
        data = json.loads(resp.data)
        assert data['count'] == 2

        db.session.delete(user_1)
        db.session.commit()

        resp = self.client.get('/user/')
        data = json.loads(resp.data)
        assert data['count'] == 1

        stored_user = data['users'][0]
        assert stored_user['id'] == user_2.id
        assert stored_user['display_name'] == user_2.display_name
        assert 'email' not in stored_user


user_test_suite = unittest.TestLoader().loadTestsFromTestCase(UserTestCase)
