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
        logger.error(f"Failed to create user from webhook (delivery_id: {delivery_id}): {e}", exc_info=True)
        raise


def handle_user_verified(payload: dict[str, Any], delivery_id: str) -> None:
    """Process user.verified webhook event.

    This event is triggered when a user verifies their email address.

    Args:
        payload: Webhook payload containing:
            - user_id (int): MusicBrainz row ID of the user
            - email (str): Verified email address
            - verified_at (str): ISO 8601 timestamp of verification
        delivery_id: Unique identifier for this webhook delivery (UUID)

    Note:
        Implementation pending - CritiqueBrainz doesn't currently track
        email verification status separately.
    """
    logger.info(f"Processing user.verified event (delivery_id: {delivery_id})")
    logger.warning(f"user.verified handler not yet implemented (delivery_id: {delivery_id})")
    # TODO: Implement email verification tracking if needed


def handle_user_updated(payload: dict[str, Any], delivery_id: str) -> None:
    """Process user.updated webhook event.

    This event is triggered when a user updates their profile information
    on the OAuth provider.

    Args:
        payload: Webhook payload structure TBD by OAuth provider
        delivery_id: Unique identifier for this webhook delivery (UUID)

    Note:
        Implementation pending - event structure not yet defined by provider.
    """
    logger.info(f"Processing user.updated event (delivery_id: {delivery_id})")
    logger.warning(f"user.updated handler not yet implemented (delivery_id: {delivery_id})")
    # TODO: Implement when OAuth provider adds this event type


def handle_user_deleted(payload: dict[str, Any], delivery_id: str) -> None:
    """Process user.deleted webhook event.

    This event is triggered when a user deletes their account on the
    OAuth provider (GDPR compliance).

    Args:
        payload: Webhook payload structure TBD by OAuth provider
        delivery_id: Unique identifier for this webhook delivery (UUID)

    Note:
        Implementation pending - event structure not yet defined by provider.
    """
    logger.info(f"Processing user.deleted event (delivery_id: {delivery_id})")
    logger.warning(f"user.deleted handler not yet implemented (delivery_id: {delivery_id})")
    # TODO: Implement when OAuth provider adds this event type


# Event handler registry
# Maps event type strings to their handler functions
EVENT_HANDLERS = {
    "user.created": handle_user_created,
    "user.verified": handle_user_verified,
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
