from __future__ import division
from itertools import izip
from math import ceil
from flask import Blueprint, render_template, request, flash, redirect, url_for, jsonify
from flask_login import login_required, current_user
from flask_babel import gettext, get_locale
from critiquebrainz.frontend.review.forms import ReviewCreateForm, ReviewEditForm, ReviewReportForm
from critiquebrainz.frontend.apis import mbspotify, musicbrainz
from critiquebrainz.data.model.review import Review
from critiquebrainz.data.model.revision import Revision
from critiquebrainz.data.model.vote import Vote
from critiquebrainz.data.model.spam_report import SpamReport
from werkzeug.exceptions import Unauthorized, NotFound
from markdown import markdown
from sqlalchemy import desc

review_bp = Blueprint('review', __name__)

RESULTS_LIMIT = 10


@review_bp.route('/')
def browse():
    page = int(request.args.get('page', default=1))
    if page < 1:
        return redirect(url_for('.browse'))
    limit = 3 * 9  # 9 rows
    offset = (page - 1) * limit
    reviews, count = Review.list(sort='created', limit=limit, offset=offset)

    if not reviews:
        if page - 1 > count / limit:
            return redirect(url_for('review.browse', page=int(ceil(count/limit))))
        else:
            raise NotFound(gettext("No reviews to display."))

    # Loading info about release groups for reviews
    rg_mbids = [review.release_group for review in reviews]
    rg_info = musicbrainz.get_multiple_release_groups(rg_mbids)

    return render_template('review/browse.html', reviews=reviews, release_groups=rg_info,
                           page=page, limit=limit, count=count)


@review_bp.route('/<uuid:id>/revisions/<int:rev>')
@review_bp.route('/<uuid:id>')
def entity(id, rev=None):
    review = Review.query.get_or_404(str(id))
    # Not showing review if it isn't published yet and not viewed by author.
    if review.is_draft and not (current_user.is_authenticated()
                                and current_user == review.user):
        raise NotFound(gettext("Can't find a review with the specified ID."))

    spotify_mappings = mbspotify.mappings(review.release_group)

    revisions = Revision.query.filter_by(review=review)
    count = revisions.count()
    if not rev:
        rev = count
    if rev < count:
        flash(gettext('You are viewing an old revision, the review has been updated since then.'))
    elif rev > count:
        raise NotFound(gettext("The revision you are looking for does not exist."))

    revision = revisions.offset(count-rev).first()
    if not review.is_draft and current_user.is_authenticated():  # if user is logged in, get his vote for this review
        vote = Vote.query.filter_by(user=current_user, revision=revision).first()
    else:  # otherwise set vote to None, its value will not be used
        vote = None
    review.text_html = markdown(revision.text, safe_mode="escape")
    return render_template('review/entity.html', review=review, spotify_mappings=spotify_mappings, vote=vote)


@review_bp.route('/<uuid:id>/revisions')
def revisions(id):
    review = Review.query.get_or_404(str(id))

    # Not showing review if it isn't published yet and not viewed by author.
    if review.is_draft and not (current_user.is_authenticated()
                                and current_user == review.user):
        raise NotFound("Can't find a review with the specified ID.")

    revisions = Revision.query.filter_by(review=review)
    count = revisions.count()
    revisions = revisions.order_by(desc(Revision.timestamp)).limit(RESULTS_LIMIT)
    results = list(izip(reversed(range(count-RESULTS_LIMIT, count)), revisions))

    return render_template('review/revisions.html', review=review, results=results, count=count, limit=RESULTS_LIMIT)


@review_bp.route('/<uuid:id>/revisions/more')
def revisions_more(id):
    review = Review.query.get_or_404(str(id))

    # Not showing review if it isn't published yet and not viewed by author.
    if review.is_draft and not (current_user.is_authenticated()
                                and current_user == review.user):
        raise NotFound("Can't find a review with the specified ID.")

    page = int(request.args.get('page', default=0))
    offset = page * RESULTS_LIMIT

    revisions = Revision.query.filter_by(review=review)
    count = revisions.count()
    revisions = revisions.order_by(desc(Revision.timestamp)).offset(offset).limit(RESULTS_LIMIT)
    results = list(izip(reversed(range(count-offset-RESULTS_LIMIT, count-offset)), revisions))

    template = render_template('review/revision_results.html', review=review, results=results)
    return jsonify(results=template, more=(count-offset-RESULTS_LIMIT) > 0)


@review_bp.route('/write', methods=('GET', 'POST'))
@login_required
def create():
    release_group = request.args.get('release_group')
    if not release_group:
        flash(gettext("Please choose release group that you want to review."))
        return redirect(url_for('search.selector', next=url_for('.create')))

    # Checking if the user already wrote a review for this release group
    review = Review.query.filter_by(user=current_user, release_group=release_group).first()
    if review:
        flash(gettext("You have already published a review for this album!"), 'error')
        return redirect(url_for('review.entity', id=review.id))

    form = ReviewCreateForm(default_language=get_locale())

    if form.validate_on_submit():
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

    release_group_details = musicbrainz.get_release_group_by_id(release_group)
    if not release_group_details:
        flash(gettext("You can only write a review for a release group that exists on MusicBrainz!"), 'error')
        return redirect(url_for('search.selector', next=url_for('.create')))
    return render_template('review/write.html', form=form, release_group=release_group_details)


@review_bp.route('/write/preview', methods=['POST'])
@login_required
def preview():
    """Get markdown preview of a text."""
    return markdown(request.form['text'], safe_mode="escape")


@review_bp.route('/<uuid:id>/edit', methods=('GET', 'POST'))
@login_required
def edit(id):
    review = Review.query.get_or_404(str(id))
    if review.is_draft and current_user != review.user:
        raise NotFound(gettext("Can't find a review with the specified ID."))
    if review.user != current_user:
        raise Unauthorized(gettext("Only author can edit this review."))

    form = ReviewEditForm(default_license_id=review.license_id, default_language=review.language)
    if not review.is_draft:
        # Can't change license if review is published.
        del form.license_choice

    if form.validate_on_submit():
        if review.is_draft:
            license_choice = form.license_choice.data
        else:
            license_choice = None
        review.update(text=form.text.data, is_draft=(form.state.data == 'draft'),
                      license_id=license_choice, language=form.language.data)
        flash(gettext("Review has been updated."), 'success')
        return redirect(url_for('.entity', id=review.id))
    else:
        form.text.data = review.text
    return render_template('review/edit.html', form=form, review=review)


@review_bp.route('/<uuid:id>/delete', methods=['GET', 'POST'])
@login_required
def delete(id):
    review = Review.query.get_or_404(str(id))
    if review.user != current_user:
        raise Unauthorized(gettext("Only the author can delete this review."))
    if request.method == 'POST':
        review.delete()
        flash(gettext("Review has been deleted."), 'success')
        return redirect(url_for('user.reviews', user_id=current_user.id))
    return render_template('review/delete.html', review=review)


@review_bp.route('/<uuid:review_id>/vote', methods=['POST'])
@login_required
def vote_submit(review_id):
    review_id = str(review_id)
    if 'yes' in request.form:
        vote = True
    elif 'no' in request.form:
        vote = False

    review = Review.query.get_or_404(review_id)
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


@review_bp.route('/<uuid:id>/vote/delete', methods=['GET'])
@login_required
def vote_delete(id):
    review = Review.query.get_or_404(str(id))
    vote = Vote.query.filter_by(user=current_user, revision=review.last_revision).first()
    if not vote:
        flash(gettext("This review is not rated yet."), 'error')
    else:
        vote.delete()
        flash(gettext("You have deleted your vote for this review!"), 'success')
    return redirect(url_for('.entity', id=id))


@review_bp.route('/<uuid:id>/report', methods=['GET', 'POST'])
@login_required
def report(id):
    review = Review.query.get_or_404(str(id))
    if review.user == current_user:
        flash(gettext("You cannot report your own review."), 'error')
        return redirect(url_for('.entity', id=id))

    last_revision_id = review.last_revision.id
    count = SpamReport.query.filter_by(user=current_user, revision_id=last_revision_id).count()
    if count > 0:
        flash(gettext("You have already reported this review."), 'error')
        return redirect(url_for('.entity', id=id))

    form = ReviewReportForm()
    if form.validate_on_submit():
        SpamReport.create(last_revision_id, current_user, form.reason.data)
        flash(gettext("Review has been reported."), 'success')
        return redirect(url_for('.entity', id=id))

    return render_template('review/report.html', review=review, form=form)
