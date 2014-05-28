from flask.ext.testing import TestCase

from critiquebrainz import create_app
from critiquebrainz.db import db, User, License, Review
import test_config


class LicenceTestCase(TestCase):
    def create_app(self):
        return create_app(test_config)

    def setUp(self):
        db.create_all()

    def tearDown(self):
        db.session.remove()
        db.drop_all()

    def test_licence_creation(self):
        license = License(id=u"Test", full_name=u'Test License')
        db.session.add(license)
        db.session.commit()
        assert License.query.count() == 1

    def test_licence_removal(self):
        license = License(id=u"Test", full_name=u'Test License')
        db.session.add(license)
        db.session.commit()

        assert License.query.count() == 1
        license.delete()
        assert License.query.count() == 0
