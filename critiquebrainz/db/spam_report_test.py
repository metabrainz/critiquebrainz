from critiquebrainz.data.testing import DataTestCase
import critiquebrainz.db.spam_report as db_spam_report
import critiquebrainz.db.review as db_review
import critiquebrainz.db.license as db_license
import critiquebrainz.db.users as db_users
from critiquebrainz.db.user import User


class SpamReportTestCase(DataTestCase):

    def setUp(self):
        super(SpamReportTestCase, self).setUp()
        author = User(db_users.get_or_create('0', new_user_data={
            "display_name": "Author",
        }))
        self.user1 = User(db_users.get_or_create('1', new_user_data={
            "display_name": "Tester #1",
        }))
        self.user2 = User(db_users.get_or_create('2', new_user_data={
            "display_name": "Tester #2",
        }))
        license = db_license.create(
            id='Test',
            full_name='Test License',
        )
        self.review = db_review.create(
            entity_id="e7aad618-fa86-3983-9e77-405e21796eca",
            entity_type="release_group",
            text="Testing!",
            user_id=author.id,
            is_draft=False,
            license_id=license["id"],
        )
        self.revision_id = self.review["last_revision"]["id"]
        self.report = db_spam_report.create(self.revision_id, self.user1.id, "To test is this report")
        self.report_time = self.report["reported_at"]

    def test_get(self):
        report = db_spam_report.get(self.user1.id, self.revision_id)
        report["user_id"] = str(report["user_id"])
        self.assertDictEqual(report, {
            "user_id": self.user1.id,
            "revision_id": self.revision_id,
            "reported_at": self.report_time,
            "reason": "To test is this report",
            "is_archived": False,
        })

    def test_archive(self):
        db_spam_report.archive(self.user1.id, self.revision_id)
        report = db_spam_report.get(self.user1.id, self.revision_id)
        self.assertEqual(report['is_archived'], True)

    def test_create(self):
        report = db_spam_report.create(self.revision_id, self.user2.id, "This is a report")
        self.assertEqual(report["reason"], "This is a report")

    def test_list_reports(self):
        db_spam_report.create(self.revision_id, self.user2.id, "This is a report")
        db_review.update(
            review_id=self.review["id"],
            drafted=self.review["is_draft"],
            text="Updated Review",
        )
        self.review = db_review.get_by_id(self.review["id"])
        db_spam_report.create(self.review["last_revision"]["id"], self.user1.id, "This is again a report on the updated review")
        # two reports on the old revision and one on the new revision.
        reports, count = db_spam_report.list_reports(review_id=self.review["id"])  # pylint: disable=unused-variable
        self.assertEqual(count, 3)
        # get all reports by a user.
        reports, count = db_spam_report.list_reports(user_id=self.user2.id)
        self.assertEqual(count, 1)
        # archive and include all archived reports.
        # there must be two reports including the archived one.
        db_spam_report.archive(self.user1.id, self.review["last_revision"]["id"])
        reports, count = db_spam_report.list_reports(inc_archived=True)
        self.assertEqual(count, 3)
        # there must be one reports excluding the archived one.
        reports, count = db_spam_report.list_reports(inc_archived=False)
        self.assertEqual(count, 2)
