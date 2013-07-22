from flask import Blueprint, flash, request, redirect, url_for, session, render_template
from flask.ext.login import login_user, logout_user, login_required
from critiquebrainz.db import User
from providers import *
from . import login_forbidden

login = Blueprint('login', __name__, url_prefix='/login')

@login.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('ui.index'))
    
@login.route('/', endpoint='index')
@login_forbidden
def login_handler():
    return render_template('login/login.html')
    
@login.route('/twitter', endpoint='twitter')
@login_forbidden
def login_twitter_handler():
    next = request.args.get('next') or \
           request.referrer or \
           url_for('ui.index')
    callback_url = url_for('.twitter_post', next=next, _external=True)
    return twitter.authorize(callback=callback_url)
    
@login.route('/twitter/post', endpoint='twitter_post')
@login_forbidden
@twitter.authorized_handler
def login_twitter_post_handler(resp):
    if resp is None:
        flash('You denied the request to sign in.')
        return redirect(url_for('.index'))

    user = User.get_or_create(display_name=resp.get('screen_name'),
        twitter_id=resp.get('user_id'))
    login_user(user)
    return redirect(request.args.get('next'))
    
@login.route('/musicbrainz', endpoint='musicbrainz')
@login_forbidden
def login_musicbrainz_handler():
    next = request.args.get('next') or \
           request.referrer or \
           url_for('ui.index')
    session['musicbrainz_next'] = next
    callback_url = url_for('.musicbrainz_post', _external=True)
    return musicbrainz.authorize(callback=callback_url)

@login.route('/musicbrainz/post', endpoint='musicbrainz_post')
@login_forbidden
@musicbrainz.authorized_handler
def login_musicbrainz_post_handler(resp):
    if resp is None:
        flash('You denied the request to sign in.')
        return redirect(url_for('.index'))

    next = session.pop('musicbrainz_next')

    # fetch musicbrainz account info
    session['musicbrainz_token'] = (resp['access_token'], '')
    me = musicbrainz.get('/oauth2/userinfo').data

    user = User.get_or_create(display_name=me.get('sub'),
        musicbrainz_id=me.get('sub'))
    login_user(user)
    return redirect(next)
