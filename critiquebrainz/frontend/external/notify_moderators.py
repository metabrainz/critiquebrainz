from brainzutils.mail import send_mail
from flask import current_app, render_template, url_for
from critiquebrainz.db import users as db_users


def mail_review_report(user, reason, review):
    report_email_address = current_app.config.get('ADMIN_NOTIFICATION_EMAIL_ADDRESS')
    if report_email_address:
        text = render_template(
            "emails/review_report.txt",
            username=user.display_name,
            review_link=url_for("review.entity", id=review["id"]),
            review_author=review["user"].display_name,
            reason=reason,
        )
        send_mail(
            subject="CritiqueBrainz Spam Review Report",
            text=text,
            recipients=report_email_address,
            from_name="CritiqueBrainz noreply",
            from_addr=current_app.config['MAIL_FROM_ADDR']
        )
