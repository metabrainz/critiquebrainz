from flask import Blueprint


def register_blueprints(app, url_prefix='/ws/1'):
    from oauth.views import oauth_bp
    from review.views import review_bp
    from user.views import user_bp

    app.register_blueprint(oauth_bp, url_prefix='%s/oauth' % url_prefix)
    app.register_blueprint(review_bp, url_prefix='%s/review' % url_prefix)
    app.register_blueprint(user_bp, url_prefix='%s/user' % url_prefix)


class WebServiceBlueprint(Blueprint):
    pass
