from critiquebrainz.data.testing import DataTestCase
from critiquebrainz.data import db
from critiquebrainz.data.model.review import Review
from critiquebrainz.data.model.license import License
import critiquebrainz.db.moderation_log as db_moderation_log
from critiquebrainz.db.moderation_log import ACTION_BLOCK_USER, ACTION_HIDE_REVIEW
from critiquebrainz.db.user import User
import critiquebrainz.db.users as db_users


class ModerationLogCase(DataTestCase):

    def setUp(self):
        super(ModerationLogCase, self).setUp()

        self.admin = User(db_users.get_or_create("Admin", new_user_data={
            "display_name":"Admin",
        }))
        self.user = User(db_users.get_or_create("Tester",new_user_data={
            "display_name":"Tester",
        }))

        self.reason = "Testing!"
        self.license = License(id="Test", full_name="Test License")
        db.session.add(self.license)
        db.session.flush()

        self.review = Review.create(
            user_id=self.user.id,
            release_group="e7aad618-fa86-3983-9e77-405e21796eca",
            text="It is beautiful!",
            is_draft=False,
            license_id=self.license.id,
            language='en',
        )

    def test_creation(self):
        db_moderation_log.create(
            admin_id=self.admin.id,
            reason=self.reason,
            user_id=self.user.id,
            action=ACTION_BLOCK_USER,
        )
        logs, count = db_moderation_log.list_logs()
        self.assertEqual(count, 1)
        self.assertEqual(str(logs[0]["user"]["id"]), self.user.id)
        self.assertEqual(str(logs[0]["admin"]["id"]), self.admin.id)

    def test_list(self):
        db_moderation_log.create(
            admin_id=self.admin.id,
            reason=self.reason,
            review_id=self.review.id,
            action=ACTION_HIDE_REVIEW,
        )
        logs, count = db_moderation_log.list_logs(admin_id=self.admin.id)
        self.assertEqual(count, 1)
        self.assertEqual(str(logs[0]["admin"]["id"]), self.admin.id)
        db_moderation_log.create(
            admin_id=self.admin.id,
            reason="User to be blocked",
            user_id=self.user.id,
            action=ACTION_BLOCK_USER,
        )
        logs, count = db_moderation_log.list_logs(admin_id=self.admin.id)
        self.assertEqual(count, 2)
