import logging
from logging.handlers import RotatingFileHandler, SMTPHandler


def add_all_loggers(app):
    add_file_handler(app, app.config['LOG_FILE'])
    add_email_handler(app)


def add_file_handler(app, filename, max_bytes=512 * 1024, backup_count=100):
    """Adds file logging."""
    file_handler = RotatingFileHandler(filename, maxBytes=max_bytes, backupCount=backup_count)
    file_handler.setFormatter(logging.Formatter(
        '%(asctime)s %(levelname)s: %(message)s '
        '[in %(pathname)s:%(lineno)d]'
    ))
    app.logger.addHandler(file_handler)


def add_email_handler(app):
    """Adds email notifications."""
    credentials = None
    if 'MAIL_USERNAME' in app.config or 'MAIL_PASSWORD' in app.config:
        credentials = (app.config['MAIL_USERNAME'], app.config['MAIL_PASSWORD'])
    mail_handler = SMTPHandler(
        (app.config['MAIL_SERVER'], app.config['MAIL_PORT']),
        app.config['MAIL_FROM_ADDR'],
        app.config['ADMINS'],
        app.config['LOG_EMAIL_TOPIC'],
        credentials)
    mail_handler.setLevel(logging.ERROR)

    mail_handler.setFormatter(logging.Formatter('''
    Message type: %(levelname)s
    Location: %(pathname)s:%(lineno)d
    Module: %(module)s
    Function: %(funcName)s
    Time: %(asctime)s

    Message:

    %(message)s
    '''))

    app.logger.addHandler(mail_handler)
