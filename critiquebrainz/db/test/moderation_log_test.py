import critiquebrainz.db.license as db_license
import critiquebrainz.db.moderation_log as db_moderation_log
import critiquebrainz.db.review as db_review
import critiquebrainz.db.users as db_users
from critiquebrainz.data.testing import DataTestCase
from critiquebrainz.db.moderation_log import AdminActions
from critiquebrainz.db.user import User


class ModerationLogTestCase(DataTestCase):

    def setUp(self):
        super(ModerationLogTestCase, self).setUp()

        self.admin = User(db_users.get_or_create(1, "Admin", new_user_data={
            "display_name": "Admin",
        }))
        self.user = User(db_users.get_or_create(2, "Tester", new_user_data={
            "display_name": "Tester",
        }))
        self.reason = "Testing!"
        self.license = db_license.create(
            id=u'TEST',
            full_name=u"Test License",
        )

        self.review = db_review.create(
            user_id=self.user.id,
            entity_id="e7aad618-fa86-3983-9e77-405e21796eca",
            entity_type="release_group",
            text="It is beautiful!",
            is_draft=False,
            license_id=self.license["id"],
            language='en',
        )

    def test_creation(self):
        # test log creation when no review_id and no user_id is given
        with self.assertRaises(ValueError) as err:
            db_moderation_log.create(
                admin_id=self.admin.id,
                reason=self.reason,
                action=AdminActions.ACTION_HIDE_REVIEW,
            )
        self.assertEqual(str(err.exception), "No review ID or user ID specified.")

        # test log creation for non existing action
        with self.assertRaises(ValueError) as err:
            db_moderation_log.create(
                admin_id=self.admin.id,
                reason=self.reason,
                user_id=self.user.id,
                action="unknown_action",
            )
        self.assertEqual(str(err.exception), "Please specify a valid action.")

        # test sample log creation for blocking user
        db_moderation_log.create(
            admin_id=self.admin.id,
            reason=self.reason,
            user_id=self.user.id,
            action=AdminActions.ACTION_BLOCK_USER,
        )
        logs, count = db_moderation_log.list_logs()
        self.assertEqual(count, 1)
        self.assertEqual(str(logs[0]["user"]["id"]), self.user.id)
        self.assertEqual(str(logs[0]["admin"]["id"]), self.admin.id)
        self.assertEqual(str(logs[0]["action"]), AdminActions.ACTION_BLOCK_USER.value)

    def test_list(self):
        # test logs for hiding review
        db_moderation_log.create(
            admin_id=self.admin.id,
            reason=self.reason,
            review_id=self.review["id"],
            action=AdminActions.ACTION_HIDE_REVIEW,
        )
        logs, count = db_moderation_log.list_logs(admin_id=self.admin.id)
        self.assertEqual(count, 1)
        self.assertEqual(str(logs[0]["admin"]["id"]), self.admin.id)
        self.assertEqual(str(logs[0]["review"]["id"]), str(self.review["id"]))
        self.assertEqual(str(logs[0]["action"]), AdminActions.ACTION_HIDE_REVIEW.value)

        # test logs for unhiding review
        db_moderation_log.create(
            admin_id=self.admin.id,
            reason=self.reason,
            review_id=self.review["id"],
            action=AdminActions.ACTION_UNHIDE_REVIEW,
        )
        logs, count = db_moderation_log.list_logs(admin_id=self.admin.id)
        self.assertEqual(count, 2)
        self.assertEqual(str(logs[0]["admin"]["id"]), self.admin.id)
        self.assertEqual(str(logs[0]["review"]["id"]), str(self.review["id"]))
        self.assertEqual(str(logs[0]["action"]), AdminActions.ACTION_UNHIDE_REVIEW.value)

        # test logs for blocking user
        db_moderation_log.create(
            admin_id=self.admin.id,
            reason="User to be blocked",
            user_id=self.user.id,
            action=AdminActions.ACTION_BLOCK_USER,
        )
        logs, count = db_moderation_log.list_logs(admin_id=self.admin.id)
        self.assertEqual(count, 3)
        self.assertEqual(str(logs[0]["admin"]["id"]), self.admin.id)
        self.assertEqual(str(logs[0]["user"]["id"]), self.user.id)
        self.assertEqual(str(logs[0]["action"]), AdminActions.ACTION_BLOCK_USER.value)

        # test logs for unblocking user
        db_moderation_log.create(
            admin_id=self.admin.id,
            reason="User to be unblocked",
            user_id=self.user.id,
            action=AdminActions.ACTION_UNBLOCK_USER,
        )
        logs, count = db_moderation_log.list_logs(admin_id=self.admin.id)
        self.assertEqual(count, 4)
        self.assertEqual(str(logs[0]["admin"]["id"]), self.admin.id)
        self.assertEqual(str(logs[0]["user"]["id"]), self.user.id)
        self.assertEqual(str(logs[0]["action"]), AdminActions.ACTION_UNBLOCK_USER.value)
