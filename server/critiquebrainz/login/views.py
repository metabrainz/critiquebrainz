from flask import Blueprint, request, redirect, session, url_for
from critiquebrainz.oauth import oauth
from critiquebrainz.exceptions import LoginError
from critiquebrainz.utils import build_url, generate_string
from critiquebrainz.login import musicbrainz, twitter

bp = Blueprint('login', __name__)

@bp.route('/musicbrainz', endpoint='musicbrainz')
def login_musicbrainz_handler():
    (client_id, _, redirect_uri, scope, state) = login_parse_parameters()
    musicbrainz.persist_data(query=(client_id, redirect_uri, scope, state))
    url = musicbrainz.get_authentication_uri()
    return redirect(url)

@bp.route('/musicbrainz/post', endpoint='musicbrainz_post')
def login_musicbrainz_post_handler():
    (client_id, redirect_uri, scope, state) = musicbrainz.fetch_data('query')

    try:
        musicbrainz.validate_post_login()
    except LoginError as e:
        raise LoginError(e.code, build_url(redirect_uri, dict(state=state)))
    except Exception:
        raise LoginError('server_error', build_url(redirect_uri, dict(state=state)))

    user_id = musicbrainz.get_user().id
    (code, ) = oauth.generate_grant(client_id, scope, redirect_uri, user_id)
    
    return redirect(build_url(redirect_uri, dict(state=state, code=code)))

@bp.route('/twitter', endpoint='twitter')
def login_twitter_handler():
    (client_id, _, redirect_uri, scope, state) = login_parse_parameters()
    twitter.persist_data(query=(client_id, redirect_uri, scope, state))
    url = twitter.get_authentication_uri()
    return redirect(url)

@bp.route('/twitter/post', endpoint='twitter_post')
def login_twitter_post_handler():
    (client_id, redirect_uri, scope, state) = twitter.fetch_data('query')

    try:
        twitter.validate_post_login()
    except LoginError as e:
        raise LoginError(e.code, build_url(redirect_uri, dict(state=state)))
    except Exception:
        raise LoginError('server_error', build_url(redirect_uri, dict(state=state)))

    user_id = twitter.get_user().id
    (code, ) = oauth.generate_grant(client_id, scope, redirect_uri, user_id)

    return redirect(build_url(redirect_uri, dict(state=state, code=code)))

@bp.errorhandler(LoginError)
def login_error_handler(error):
    if error.redirect_uri:
        return redirect(build_url(error.redirect_uri, dict(error=error.code)))
    else:
        return error.code

@bp.errorhandler(Exception)
def exception_handler(error):
    redirect_uri = request.args.get('redirect_uri')
    return login_error_handler(LoginError('server_error', redirect_uri))

def login_parse_parameters():
    client_id = request.args.get('client_id')
    response_type = request.args.get('response_type')
    redirect_uri = request.args.get('redirect_uri')
    scope = request.args.get('scope')
    state = request.args.get('state')

    # validate request
    oauth.validate_authorization_request(client_id, response_type, redirect_uri, scope)

    # client MUST define `authorization` in the scope
    scopes = scope.split()
    if 'authorization' not in scopes:
        raise LoginError('access_denied', redirect_uri)

    return (client_id, response_type, redirect_uri, scope, state)
