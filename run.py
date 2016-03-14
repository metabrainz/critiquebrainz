from werkzeug.serving import run_simple
from werkzeug.wsgi import DispatcherMiddleware
from critiquebrainz.frontend import create_app as frontend_create_app
from critiquebrainz.ws import create_app as ws_create_app

application = DispatcherMiddleware(frontend_create_app(), {
    '/ws/1': ws_create_app()
})

if __name__ == '__main__':
    run_simple('0.0.0.0', 8080, application,
               use_reloader=True, use_debugger=True, use_evalex=True)
