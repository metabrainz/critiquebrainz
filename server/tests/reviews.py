import json

from flask.ext.testing import TestCase

from critiquebrainz import create_app
from critiquebrainz.db import db, User, License, Review


class Reviews(TestCase):
    def create_app(self):
        import test_config
        app = create_app(test_config)
        import manage
        manage.init_postgres(test_config.SQLALCHEMY_DATABASE_URI)
        return app

    def setUp(self):
        db.create_all()

    def tearDown(self):
        db.session.remove()
        db.drop_all()

    def test_empty_db(self):
        resp = self.client.get('/review/')
        data = json.loads(resp.data)
        assert data['count'] == 0

    def test_review_addition(self):
        # Review needs user
        user = User(display_name=u'Tester')
        db.session.add(user)
        db.session.commit()

        # and license
        license = License(id=u"Test", full_name=u'Test License')
        db.session.add(license)
        db.session.commit()

        # Creating new review
        text = u"Testing!"
        review = Review.create(user=user,
                               release_group='e7aad618-fa86-3983-9e77-405e21796eca',
                               text=text,
                               license_id=license.id)
        db.session.add(review)
        db.session.commit()
        resp = self.client.get('/review/')
        data = json.loads(resp.data)
        assert data['count'] == 1
        assert len(data['reviews']) == 1
        stored_review = data['reviews'][0]
        assert stored_review['id'] == review.id
        assert stored_review['release_group'] == review.release_group
        assert stored_review['text'] == text
        assert stored_review['license']['id'] == license.id
        assert stored_review['license']['full_name'] == license.full_name