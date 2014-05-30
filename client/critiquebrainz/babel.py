from flask import g, request
from flask.ext.babel import Babel
from critiquebrainz import app
from config import LANGUAGES

babel = Babel(app)


@babel.localeselector
def get_locale():
    # if a user is logged in, use the locale from the user settings
    user = getattr(g, 'user', None)
    if user is not None:
        return user.locale

    # otherwise try to guess the language from the user accept header the browser transmits.
    return request.accept_languages.best_match(LANGUAGES.keys())