import logging
from logging.handlers import RotatingFileHandler, SMTPHandler
from config import ADMINS, MAIL_SERVER, MAIL_PORT, MAIL_USERNAME, MAIL_PASSWORD, LOG_EMAIL_TOPIC


def init_app(app):
    # File logging
    handler = RotatingFileHandler(app.config['LOG_FILE'], maxBytes=512 * 1024, backupCount=100)
    app.logger.addHandler(handler)

    # Email
    credentials = None
    if MAIL_USERNAME or MAIL_PASSWORD:
        credentials = (MAIL_USERNAME, MAIL_PASSWORD)
    mail_handler = SMTPHandler((MAIL_SERVER, MAIL_PORT), 'no-reply@'+MAIL_SERVER, ADMINS, LOG_EMAIL_TOPIC, credentials)
    mail_handler.setLevel(logging.ERROR)
    app.logger.addHandler(mail_handler)