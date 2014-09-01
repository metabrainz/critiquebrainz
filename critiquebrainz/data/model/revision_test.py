from critiquebrainz.data.testing import DataTestCase
from critiquebrainz.data import db
from user import User
from license import License
from review import Review


class RevisionTestCase(DataTestCase):

    def setUp(self):
        super(RevisionTestCase, self).setUp()

        self.user = User(display_name=u'Tester')
        db.session.add(self.user)
        db.session.commit()

        self.license = License(id=u'TEST', full_name=u"Test License")
        db.session.add(self.license)
        db.session.commit()

        self.review = Review.create(user=self.user,
                                    release_group='e7aad618-fa86-3983-9e77-405e21796eca',
                                    text=u"Testing!",
                                    is_draft=False,
                                    license_id=self.license.id)

    def test_to_dict(self):
        revision = self.review.revisions[0]
        self.assertDictEqual(revision.to_dict(), dict(id=revision.id,
                                                      review_id=revision.review_id,
                                                      timestamp=revision.timestamp,
                                                      text=revision.text))

    def test_revision_deletion(self):
        self.assertEqual(len(self.review.revisions), 1)

        self.review.revisions[0].delete()
        self.assertEqual(len(self.review.revisions), 0)
