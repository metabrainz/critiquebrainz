from brainzutils.mail import send_mail
from flask import current_app
from critiquebrainz.db import users as db_users


def mail_review_report(user, reason, review):
    mod_usernames = set(map(str.lower, current_app.config['ADMINS']))  # MusicBrainz usernames
    mods_data = db_users.get_many_by_mb_username(list(mod_usernames))
    for mod_data in mods_data:
        # Removing from `mod_usernames` to figure out which mods don't have a CB account afterwards
        if mod_data["musicbrainz_username"].lower() in mod_usernames:
            mod_usernames.remove(mod_data["musicbrainz_username"].lower())

    mod_emails = []
    for mod_data in mods_data:
        if mod_data["email"]:
            mod_emails.append(mod_data["email"])
    text = ("Hi CritiqueBrainz moderator!"
            "{username} has just reported a spam review by {review_author}"
            "Reason for report: {reason}."
            "Please take a look at reports page for more information.\n"
            "- The CritiqueBrainz Team").format(
                username=user.display_name,
                review_author=review["user"].display_name,
                reason=reason,
            )
    if mod_emails:
        send_mail(
            subject="CritiqueBrainz Spam Review Report",
            text=text,
            recipients=[mod_emails],
        )
