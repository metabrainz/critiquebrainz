from critiquebrainz.data.testing import DataTestCase
from critiquebrainz.data import db
from critiquebrainz.data.model.revision import Revision
from critiquebrainz.data.model.user import User
from critiquebrainz.data.model.license import License
from critiquebrainz.data.model.review import Review


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
                                                      votes_positive=revision.votes_positive_count,
                                                      votes_negative=revision.votes_negative_count,
                                                      text=revision.text))

    def test_revision_deletion(self):
        self.assertEqual(Revision.query.count(), 1)  # Got one from review created in setUp method

        new_revision = Revision()
        new_revision.review_id = self.review.id
        new_revision.text = u"Testing something else!"
        db.session.add(new_revision)
        db.session.commit()

        self.assertEqual(Revision.query.count(), 2)

        new_revision.delete()

        self.assertEqual(Revision.query.count(), 1)
