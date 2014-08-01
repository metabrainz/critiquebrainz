def register_blueprints(app):
    from views import frontend_bp
    from review.views import review_bp
    from search.views import search_bp
    from artist.views import artist_bp
    from release_group.views import release_group_bp
    from matching.views import matching_bp
    from user.views import user_bp
    from profile.views import profile_bp
    from profile.applications.views import profile_apps_bp
    from login.views import login_bp
    from oauth.views import oauth_bp

    app.register_blueprint(frontend_bp)
    app.register_blueprint(review_bp, url_prefix='/review')
    app.register_blueprint(search_bp, url_prefix='/search')
    app.register_blueprint(artist_bp, url_prefix='/artist')
    app.register_blueprint(release_group_bp, url_prefix='/release-group')
    app.register_blueprint(matching_bp, url_prefix='/matching')
    app.register_blueprint(user_bp, url_prefix='/user')
    app.register_blueprint(profile_bp, url_prefix='/profile')
    app.register_blueprint(profile_apps_bp, url_prefix='/profile/applications')
    app.register_blueprint(login_bp, url_prefix='/login')
    app.register_blueprint(oauth_bp, url_prefix='/oauth')
