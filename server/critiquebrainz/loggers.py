import logging
from logging.handlers import RotatingFileHandler

def init_app(app):
    handler = RotatingFileHandler(app.config['LOG_FILE'], maxBytes=512*1024, backupCount=100)
    app.logger.addHandler(handler)
