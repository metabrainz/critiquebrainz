from unittest import TestCase, mock

from critiquebrainz.db import webhook_handlers


class WebhookHandlersTestCase(TestCase):

    @mock.patch("critiquebrainz.db.webhook_handlers.db_users")
    def test_handle_user_updated_updates_username_and_email(self, db_users):
        user = {
            "id": "cb-user-id",
            "display_name": "old_name",
            "musicbrainz_username": "old_name",
            "email": "old@example.com",
        }
        updated_user = dict(user, musicbrainz_username="new_name", display_name="new_name")
        db_users.get_by_mb_row_id.return_value = user
        db_users.update_username.return_value = updated_user

        webhook_handlers.handle_user_updated({
            "user_id": 1,
            "new": {
                "name": "new_name",
                "email": "new@example.com",
            },
            "old": {
                "name": "old_name",
                "email": None,
            },
        }, "delivery-id")

        db_users.get_by_mb_row_id.assert_called_once_with(1)
        db_users.update_username.assert_called_once_with(user, "new_name")
        db_users.update.assert_called_once_with("cb-user-id", {"email": "new@example.com"})

    @mock.patch("critiquebrainz.db.webhook_handlers.db_users")
    def test_handle_user_updated_updates_email_only(self, db_users):
        user = {
            "id": "cb-user-id",
            "display_name": "old_name",
            "musicbrainz_username": "old_name",
            "email": None,
        }
        db_users.get_by_mb_row_id.return_value = user

        webhook_handlers.handle_user_updated({
            "user_id": 1,
            "new": {
                "email": "new@example.com",
            },
            "old": {
                "email": None,
            },
        }, "delivery-id")

        db_users.get_by_mb_row_id.assert_called_once_with(1)
        db_users.update_username.assert_not_called()
        db_users.update.assert_called_once_with("cb-user-id", {"email": "new@example.com"})

    @mock.patch("critiquebrainz.db.webhook_handlers.db_users")
    def test_handle_user_updated_returns_when_no_relevant_changes(self, db_users):
        webhook_handlers.handle_user_updated({
            "user_id": 1,
            "new": {
                "irrelevant": "value",
            },
        }, "delivery-id")

        db_users.get_by_mb_row_id.assert_not_called()
        db_users.update_username.assert_not_called()
        db_users.update.assert_not_called()

    @mock.patch("critiquebrainz.db.webhook_handlers.db_users")
    def test_handle_user_updated_returns_when_user_is_missing(self, db_users):
        db_users.get_by_mb_row_id.return_value = None

        webhook_handlers.handle_user_updated({
            "user_id": 1,
            "new": {
                "name": "new_name",
            },
        }, "delivery-id")

        db_users.get_by_mb_row_id.assert_called_once_with(1)
        db_users.update_username.assert_not_called()
        db_users.update.assert_not_called()

    @mock.patch("critiquebrainz.db.webhook_handlers.db_users")
    def test_handle_user_deleted_deletes_user(self, db_users):
        db_users.get_by_mb_row_id.return_value = {"id": "cb-user-id"}

        webhook_handlers.handle_user_deleted({"user_id": 1}, "delivery-id")

        db_users.get_by_mb_row_id.assert_called_once_with(1)
        db_users.delete.assert_called_once_with("cb-user-id")

    @mock.patch("critiquebrainz.db.webhook_handlers.db_users")
    def test_handle_user_deleted_returns_when_user_is_missing(self, db_users):
        db_users.get_by_mb_row_id.return_value = None

        webhook_handlers.handle_user_deleted({"user_id": 1}, "delivery-id")

        db_users.get_by_mb_row_id.assert_called_once_with(1)
        db_users.delete.assert_not_called()
