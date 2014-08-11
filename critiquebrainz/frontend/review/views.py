from flask import Blueprint, render_template, request, flash, redirect, url_for, jsonify, abort
from flask.ext.login import login_required, current_user
from flask.ext.babel import gettext, get_locale
from critiquebrainz.frontend.forms.review import ReviewCreateForm, ReviewEditForm
from critiquebrainz.frontend.apis import mbspotify, musicbrainz
from critiquebrainz.data.model.review import Review
from critiquebrainz.data.model.vote import Vote
from critiquebrainz.data.model.report import SpamReport
from critiquebrainz.frontend.exceptions import NotFound
from markdown import markdown

review_bp = Blueprint('review', __name__)


@review_bp.route('/<uuid:id>', endpoint='entity')
def review_entity_handler(id):
    review = Review.query.get_or_404(str(id))
    # Not showing review if it's archived or (isn't published yet and not viewed by author).
    if review.is_archived or (review.is_draft and not (current_user.is_authenticated() and current_user == review.user)):
        raise NotFound

    spotify_mapping = mbspotify.mapping([review.release_group])

    if not review.is_draft and current_user.is_authenticated():  # if user is logged in, get his vote for this review
        # TODO: Review this functionality. It might be confusing.
        # If users vote on review and then author updates that review (last revision changes),
        # users will be unable to see their votes.
        vote = Vote.query.filter_by(user=current_user, revision=review.last_revision).first()
    else:  # otherwise set vote to None, its value will not be used
        vote = None
    review.text_html = markdown(review.text, safe_mode="escape")
    return render_template('review/entity.html', review=review, spotify_mapping=spotify_mapping, vote=vote)


@review_bp.route('/write', methods=('GET', 'POST'), endpoint='create')
@login_required
def create_handler():
    release_group = request.args.get('release_group')
    if not release_group:
        flash('Please choose release group that you want to review.')
        return redirect(url_for('search.selector', next=url_for('.create')))

    form = ReviewCreateForm(default_language=get_locale())

    if form.validate_on_submit():
        # Checking if review has been published
        if Review.query.filter_by(user=current_user, release_group=release_group).count():
            flash(gettext("You have already published a review for this album!"), 'error')
            return redirect(url_for('user.reviews', user_id=current_user.id))

        if current_user.is_review_limit_exceeded:
            flash(gettext("You have exceeded your limit of reviews per day."), 'error')
            return redirect(url_for('user.reviews', user_id=current_user.id))

        is_draft = form.state.data == 'draft'
        review = Review.create(user=current_user, release_group=release_group, text=form.text.data,
                               license_id=form.license_choice.data, language=form.language.data,
                               is_draft=is_draft)
        if is_draft:
            flash(gettext("Review has been saved!"), 'success')
        else:
            flash(gettext("Review has been published!"), 'success')
        return redirect(url_for('.entity', id=review.id))

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
    review = Review.query.get_or_404(str(id))
    if review.is_archived or (review.is_draft and current_user != review.user):
        raise NotFound
    if review.user != current_user:
        abort(403)

    form = ReviewEditForm(default_license_id=review.license_id)
    if not review.is_draft:
        # Can't change license if review is published.
        del form.license_choice

    if form.validate_on_submit():
        review.update(text=form.text.data, is_draft=(form.state.data == 'draft'), license_id=form.license_choice.data)
        flash(gettext("Review has been updated."), 'success')
        return redirect(url_for('.entity', id=review.id))
    else:
        form.text.data = review.text
    return render_template('review/edit.html', form=form, review=review)


@review_bp.route('/<uuid:id>/delete', endpoint='delete')
@login_required
def delete_handler(id):
    review = Review.query.get_or_404(str(id))
    if review.is_archived is True:
        raise NotFound
    if review.user != current_user:
        abort(403)
    review.delete()
    flash(gettext("Review has been deleted."), 'success')
    return redirect(url_for('user.reviews', user_id=current_user.id))


@review_bp.route('/<uuid:review_id>/vote', methods=['POST'], endpoint='vote_submit')
@login_required
def review_vote_submit_handler(review_id):
    review_id = str(review_id)
    if 'yes' in request.form:
        vote = True
    elif 'no' in request.form:
        vote = False

    review = Review.query.get_or_404(review_id)
    if review.is_archived is True:
        raise NotFound
    if review.user == current_user:
        flash(gettext("You cannot rate your own review."), 'error')
        return redirect(url_for('.entity', id=review_id))
    if current_user.is_vote_limit_exceeded is True and current_user.has_voted(review) is False:
        flash(gettext("You have exceeded your limit of votes per day."), 'error')
        return redirect(url_for('.entity', id=review_id))
    if vote is True and current_user.user_type not in review.review_class.upvote:
        flash(gettext("You are not allowed to rate this review."), 'error')
        return redirect(url_for('.entity', id=review_id))
    if vote is False and current_user.user_type not in review.review_class.downvote:
        flash(gettext("You are not allowed to rate this review."), 'error')
        return redirect(url_for('.entity', id=review_id))
    Vote.create(current_user, review, vote)  # overwrites an existing vote, if needed

    flash(gettext("You have rated this review!"), 'success')
    return redirect(url_for('.entity', id=review_id))


@review_bp.route('/<uuid:id>/vote/delete', methods=['GET'], endpoint='vote_delete')
@login_required
def review_vote_delete_handler(id):
    review = Review.query.get_or_404(str(id))
    if review.is_archived is True:
        raise NotFound
    vote = Vote.query.filter_by(user=current_user, revision=review.last_revision).first()
    if not vote:
        flash(gettext("This review is not rated yet."), 'error')
    else:
        vote.delete()
        flash(gettext("You have deleted your vote for this review!"), 'success')
    return redirect(url_for('.entity', id=id))


@review_bp.route('/<uuid:id>/report', methods=['POST'], endpoint='report')
@login_required
def review_spam_report_handler(id):
    review = Review.query.get_or_404(str(id))
    if review.user == current_user:
        return jsonify(success=False, error='own')
    if review.is_archived is True:
        return jsonify(success=False, error='archived')
    last_revision_id = review.revisions[-1].id
    count = SpamReport.query.filter_by(user=current_user, revision_id=last_revision_id).count()
    if count > 0:
        return jsonify(success=False, error='reported')
    SpamReport.create(last_revision_id, current_user)
    return jsonify(success=True)
