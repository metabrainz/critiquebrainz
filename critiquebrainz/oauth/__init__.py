from provider import AuthProvider

oauth = AuthProvider()

def init_app(app):
    oauth.init_app(app)
    return oauth
