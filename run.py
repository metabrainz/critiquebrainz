from critiquebrainz import create_app
from werkzeug.serving import run_simple
from werkzeug.wsgi import DispatcherMiddleware
import werkzeug


application = DispatcherMiddleware(create_app(), {
    '/backend': create_app()
})

#application = create_app()


if __name__ == '__main__':
    run_simple('0.0.0.0', 5000, application,
               use_reloader=True, use_debugger=True, use_evalex=True)
