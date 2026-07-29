from typing import Any
import logging

import critiquebrainz.db.users as db_users

logger = logging.getLogger(__name__)


def handle_user_created(payload: dict[str, Any], delivery_id: str) -> None:
    """Process user.created webhook event.

    This event is triggered when a new user registers through the OAuth provider.
    The handler creates a corresponding user account in CritiqueBrainz.

    Args:
        payload: Webhook payload containing:
            - user_id (int): MusicBrainz row ID of the user
            - name (str): MusicBrainz username
            - email (str): User's email address
            - is_email_confirmed (bool): Email verification status
            - created_at (str): ISO 8601 timestamp of account creation
        delivery_id: Unique identifier for this webhook delivery (UUID)

    Example payload:
        {
            "user_id": 12345,
            "name": "john_doe",
            "email": "john@example.com",
            "is_email_confirmed": false,
            "created_at": "2025-11-05T10:30:00Z"
        }
    """
    logger.info(f"Processing user.created event (delivery_id: {delivery_id})")

    try:
        db_users.create(
            musicbrainz_row_id=payload["user_id"],
            display_name=payload["name"],
            musicbrainz_username=payload["name"],
            email=payload.get("email"),
        )
        logger.info(f"Successfully created user {payload['name']} (delivery_id: {delivery_id})")
    except Exception as e:
        logger.error(
            f"Failed to create user {payload["user_id"]}({payload['name']}) from webhook (delivery_id: {delivery_id}): {e}", exc_info=True)
        raise


def handle_user_updated(payload: dict[str, Any], delivery_id: str) -> None:
    """Process user.updated webhook event.

    This event is triggered when a user updates their profile information
    on the OAuth provider.

    Args:
        payload: Webhook payload containing:
            - user_id (int): MusicBrainz row ID of the user
            - old (dict): Previous values for changed fields
            - new (dict): New values for changed fields
            - updated_at (str): ISO 8601 timestamp of the update
        delivery_id: Unique identifier for this webhook delivery (UUID)
    """
    logger.info(f"Processing user.updated event (delivery_id: {delivery_id})")

    user_id = payload["user_id"]
    new_data = payload.get("new", {})

    new_username = new_data.get("name")
    has_email_update = "email" in new_data

    if not new_username and not has_email_update:
        logger.info(f"No name or email update in user.updated webhook for user_id={user_id}")
        return

    user = db_users.get_by_mb_row_id(user_id)
    if not user:
        logger.error(f"User with musicbrainz_row_id={user_id} not found for user.updated webhook")
        return

    try:
        if new_username:
            user = db_users.update_username(user, new_username)

        if has_email_update:
            db_users.update(user["id"], {"email": new_data.get("email")})

        logger.info(f"Successfully updated user {user_id} (delivery_id: {delivery_id})")
    except Exception as e:
        logger.error(f"Failed to update user {user_id} from webhook (delivery_id: {delivery_id}): {e}", exc_info=True)
        raise


def handle_user_deleted(payload: dict[str, Any], delivery_id: str) -> None:
    """Process user.deleted webhook event.

    This event is triggered when a user deletes their account on the
    OAuth provider (GDPR compliance).

    Args:
        payload: Webhook payload containing:
            - user_id (int): MusicBrainz row ID of the user
        delivery_id: Unique identifier for this webhook delivery (UUID)
    """
    logger.info(f"Processing user.deleted event (delivery_id: {delivery_id})")

    user_id = payload["user_id"]
    user = db_users.get_by_mb_row_id(user_id)
    if not user:
        logger.error(f"User with musicbrainz_row_id={user_id} not found for user.deleted webhook")
        return

    try:
        db_users.delete(user["id"])
        logger.info(f"Successfully deleted user {user_id} (delivery_id: {delivery_id})")
    except Exception as e:
        logger.error(f"Failed to delete user {user_id} from webhook (delivery_id: {delivery_id}): {e}", exc_info=True)
        raise


# Event handler registry
# Maps event type strings to their handler functions
EVENT_HANDLERS = {
    "user.created": handle_user_created,
    "user.updated": handle_user_updated,
    "user.deleted": handle_user_deleted,
}


def get_event_handler(event_type: str):
    """Get the handler function for a specific webhook event type.

    Args:
        event_type: The event type string (e.g., "user.created")

    Returns:
        The handler function for the event type, or None if not found

    Example:
        handler = get_event_handler("user.created")
        if handler:
            handler(payload, delivery_id)
    """
    return EVENT_HANDLERS.get(event_type)
