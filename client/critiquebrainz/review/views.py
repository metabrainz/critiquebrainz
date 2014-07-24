from flask import Blueprint, render_template, request, flash, redirect, url_for, jsonify
from flask.ext.login import login_required, current_user
from flask.ext.babel import gettext, Locale
from babel.core import UnknownLocaleError

from critiquebrainz.apis import musicbrainz
from critiquebrainz.forms.profile.review import ReviewCreateForm, ReviewEditForm
from critiquebrainz.babel import get_locale
import pycountry

from critiquebrainz.apis import server, mbspotify
from critiquebrainz.exceptions import ServerError, APIError, NotFound
from markdown import markdown

review_bp = Blueprint('review', __name__)


@review_bp.route('/<uuid:id>', endpoint='entity')
def review_entity_handler(id):
    try:
        review = server.get_review(id, inc=['user'])
    except ServerError as e:
        if e.code == 'not_found':
            raise NotFound(gettext("Sorry we couldn't find review with that ID."))
        else:
            raise e
    spotify_mapping = mbspotify.mapping([str(review['release_group'])])
    # if user is logged in, get his vote for this review
    if current_user.is_authenticated():
        try:
            vote = server.get_vote(id, access_token=current_user.access_token)
        except APIError as e:
            # handle the exception, if user has not rated the review yet
            if e.code == 'not_found':
                vote = None
            else:
                raise e
    # otherwise set vote to None, its value will not be used
    else:
        vote = None
    review["text"] = markdown(review["text"], safe_mode="escape")
    return render_template('review/entity.html', review=review, spotify_mapping=spotify_mapping, vote=vote)


@review_bp.route('/write', methods=('GET', 'POST'), endpoint='create')
@login_required
def create_handler():
    release_group = request.args.get('release_group')
    if not release_group:
        flash('Please choose release group that you want to review.')
        return redirect(url_for('search.selector', next=url_for('.create')))

    # Loading supported languages
    supported_languages = []
    for language_code in server.get_review_languages():
        try:
            supported_languages.append((language_code, Locale(language_code).language_name))
        except UnknownLocaleError:
            supported_languages.append((language_code, pycountry.languages.get(alpha2=language_code).name))

    form = ReviewCreateForm(languages=supported_languages, default_language=get_locale())

    if form.validate_on_submit():
        try:
            # TODO: Validate that release group exists (maybe do that on server)
            server.create_review(release_group, form.text.data, form.license_choice.data, form.language.data, current_user.access_token)
        except APIError as e:
            flash(e.desc, 'error')
        else:
            flash(gettext('You have published the review!'), 'success')
        return redirect(url_for('user.reviews', user_id=current_user.me['id']))

    release_group_details = musicbrainz.release_group_details(release_group)
    if not release_group_details:
        flash(gettext("You can only write a review for a release group that exists on MusicBrainz!"), 'error')
        return redirect(url_for('search.selector', next=url_for('.create')))
    return render_template('review/write.html', form=form, release_group=release_group_details)


@review_bp.route('/write/preview', methods=['POST'], endpoint='preview')
@login_required
def preview_handler():
    """Get markdown preview of a text."""
    return markdown(request.form['text'], safe_mode="escape")


@review_bp.route('/<uuid:id>/edit', methods=('GET', 'POST'), endpoint='edit')
@login_required
def edit_handler(id):
    review = server.get_review(str(id))
    if review.get('user') != current_user.me.get('id'):
        return redirect(url_for('index'))

    form = ReviewEditForm()
    if form.validate_on_submit():
        try:
            message = server.update_review(id, current_user.access_token, text=form.text.data)
        except APIError as e:
            flash(e.desc, 'error')
        else:
            flash(gettext('You have modified the review!'), 'success')
        return redirect(url_for('user.reviews', user_id=current_user.me['id']))
    else:
        form.text.data = review.get('text')
    return render_template('review/edit.html', form=form, review=review)


@review_bp.route('/<uuid:id>/delete', endpoint='delete')
@login_required
def delete_handler(id):
    try:
        message = server.delete_review(str(id), current_user.access_token)
    except APIError as e:
        flash(e.desc, 'error')
    else:
        flash(gettext('You have deleted the review.'), 'success')
    return redirect(url_for('user.reviews', user_id=current_user.me['id']))


@review_bp.route('/<uuid:id>/vote', methods=['POST'], endpoint='vote_submit')
@login_required
def review_vote_submit_handler(id):
    if 'yes' in request.form:
        placet = True
    elif 'no' in request.form:
        placet = False
    try:
        message = server.update_review_vote(id, current_user.access_token, placet=placet)
    except APIError as e:
        flash(e.desc, 'error')
    else:
        flash(gettext('You have rated the review!'), 'success')
    return redirect(url_for('.entity', id=id))


@review_bp.route('/<uuid:id>/vote/delete', methods=['GET'], endpoint='vote_delete')
@login_required
def review_vote_delete_handler(id):
    try:
        message = server.delete_review_vote(id, current_user.access_token)
    except APIError as e:
        flash(e.desc, 'error')
    else:
        flash(gettext('You have deleted your vote for this review!'), 'success')
    return redirect(url_for('.entity', id=id))


@review_bp.route('/<uuid:id>/report', methods=['POST'], endpoint='report')
@login_required
def review_spam_report_handler(id):
    try:
        message = server.spam_report_review(id, current_user.access_token)
    except APIError as e:
        return jsonify(success=False, error=e.desc)
    return jsonify(success=True)
