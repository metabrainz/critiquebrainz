from flask import g, request, after_this_request
from flask.ext.babel import Babel
from critiquebrainz import app
from config import LANGUAGES

babel = Babel(app)


@app.after_request
def call_after_request_callbacks(response):
    for callback in getattr(g, 'after_request_callbacks', ()):
        callback(response)
    return response


def after_this_request(f):
    if not hasattr(g, 'after_request_callbacks'):
        g.after_request_callbacks = []
    g.after_request_callbacks.append(f)
    return f


@babel.localeselector
def get_locale():
    supported_languages = LANGUAGES.keys()
    language_arg = request.args.get('l')
    if language_arg is not None:
        if language_arg in supported_languages:
            @after_this_request
            def remember_language(response):
                response.set_cookie('language', language_arg)

            return language_arg
    else:
        language_cookie = request.cookies.get('language')
        if language_cookie in supported_languages:
            return language_cookie

    return request.accept_languages.best_match(supported_languages)