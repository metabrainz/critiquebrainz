from critiquebrainz.data.testing import DataTestCase
from critiquebrainz.data import db
from critiquebrainz.data.model.user import User
from critiquebrainz.data.model.license import License
from critiquebrainz.data.model.review import Review
from critiquebrainz.data.model.spam_report import SpamReport


class SpamReportTestCase(DataTestCase):
    def setUp(self):
        super(SpamReportTestCase, self).setUp()

        # We need review and a couple of users to work with.

        self.reporter = User(display_name=u'Reporter')
        db.session.add(self.reporter)

        self.author = User(display_name=u'Author')
        db.session.add(self.author)
        self.license = License(id=u'Test', full_name=u'Test License')
        db.session.add(self.license)
        db.session.flush()

        self.review = Review.create(user_id=self.author.id, release_group='e7aad618-fa86-3983-9e77-405e21796eca',
                                    text=u"It's... beautiful!", is_draft=False, license_id=self.license.id,
                                    language='en')

    def test_spam_report_creation(self):
        # There should be no spam reports initially.
        self.assertEqual(SpamReport.query.count(), 0)

        report = SpamReport.create(self.review.last_revision.id, self.reporter.id, "Testing Reason")

        all_reports = SpamReport.query.all()
        self.assertEqual(len(all_reports), 1)
        self.assertEqual(all_reports[0].user_id, report.user_id)
        self.assertEqual(all_reports[0].revision_id, report.revision_id)

        # Let's try to add spam report using the author. This shouldn't be allowed.
        SpamReport.create(self.review.last_revision.id, self.author.id, "Testing Reason")
        self.assertEqual(len(all_reports), 1)  # hence count is the same as before

    def test_spam_report_deletion(self):
        report = SpamReport.create(self.review.last_revision.id, self.reporter.id, "Testing Reason")
        self.assertEqual(SpamReport.query.count(), 1)

        report.delete()
        self.assertEqual(SpamReport.query.count(), 0)
