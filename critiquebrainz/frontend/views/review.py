from math import ceil

from flask import Blueprint, render_template, request, flash, redirect, url_for, jsonify
from flask_babel import gettext, get_locale
from flask_login import login_required, current_user
from markdown import markdown
from sqlalchemy import desc
from werkzeug.exceptions import Unauthorized, NotFound, Forbidden, BadRequest

from critiquebrainz.data.model.moderation_log import ModerationLog, ACTION_HIDE_REVIEW
from critiquebrainz.data.model.review import Review, ENTITY_TYPES
from critiquebrainz.data.model.revision import Revision
from critiquebrainz.data.model.spam_report import SpamReport
from critiquebrainz.data.model.vote import Vote
from critiquebrainz.db import vote as db_vote, exceptions as db_exceptions
from critiquebrainz.frontend import flash
from critiquebrainz.frontend.external import mbspotify, musicbrainz, soundcloud
from critiquebrainz.frontend.forms.log import AdminActionForm
from critiquebrainz.frontend.forms.review import ReviewCreateForm, ReviewEditForm, ReviewReportForm
from critiquebrainz.frontend.login import admin_view
from critiquebrainz.utils import side_by_side_diff

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

    # Loading info about entities for reviews
    entities = [(review.entity_id, review.entity_type) for review in reviews]
    entities_info = musicbrainz.get_multiple_entities(entities)

    return render_template('review/browse.html', reviews=reviews, entities=entities_info,
                           page=page, limit=limit, count=count)


@review_bp.route('/<uuid:id>/revisions/<int:rev>')
@review_bp.route('/<uuid:id>')
def entity(id, rev=None):
    review = Review.query.get_or_404(str(id))
    # Not showing review if it isn't published yet and not viewed by author.
    if review.is_draft and not (current_user.is_authenticated
                                and current_user == review.user):
        raise NotFound(gettext("Can't find a review with the specified ID."))
    if review.is_hidden:
        if not current_user.is_admin():
            raise Forbidden(gettext("Review has been hidden. "
                                    "You need to be an administrator to view it."))
        else:
            flash.warn(gettext("Review has been hidden."))

    spotify_mappings = None
    soundcloud_url = None
    if review.entity_type == 'release_group':
        spotify_mappings = mbspotify.mappings(review.entity_id)
        soundcloud_url = soundcloud.get_url(review.entity_id)

    revisions = Revision.query.filter_by(review=review).order_by(desc(Revision.timestamp))
    count = revisions.count()
    if not rev:
        rev = count
    if rev < count:
        flash.info(gettext('You are viewing an old revision, the review has been updated since then.'))
    elif rev > count:
        raise NotFound(gettext("The revision you are looking for does not exist."))

    revision = revisions.offset(count-rev).first()
    if not review.is_draft and current_user.is_authenticated:  # if user is logged in, get their vote for this review
        try:
            vote = db_vote.get(user_id=current_user.id, revision_id=revision.id)
        except db_exceptions.NoDataFoundException:
            vote = None
    else:  # otherwise set vote to None, its value will not be used
        vote = None
    review.text_html = markdown(revision.text, safe_mode="escape")
    return render_template('review/entity/%s.html' % review.entity_type, review=review, spotify_mappings=spotify_mappings, soundcloud_url=soundcloud_url, vote=vote)


@review_bp.route('/<uuid:id>/revisions/compare')
def compare(id):
    review = Review.query.get_or_404(str(id))
    if review.is_draft and not (current_user.is_authenticated
                                and current_user == review.user):
        raise NotFound(gettext("Can't find a review with the specified ID."))
    if review.is_hidden and not current_user.is_admin():
        raise NotFound(gettext("Review has been hidden."))

    revisions = Revision.query.filter_by(review=review).order_by(desc(Revision.timestamp))
    count = revisions.count()
    old, new = int(request.args.get('old') or count - 1), int(request.args.get('new') or count)
    if old > count or new > count:
        raise NotFound(gettext("The revision(s) you are looking for does not exist."))
    if old > new:
        return redirect(url_for('.compare', id=id, old=new, new=old))

    left = revisions.offset(count-old).first()
    right = revisions.offset(count-new).first()
    left.number, right.number = old, new
    left.text, right.text = side_by_side_diff(left.text, right.text)

    return render_template('review/compare.html', review=review, left=left, right=right)


@review_bp.route('/<uuid:id>/revisions')
def revisions(id):
    review = Review.query.get_or_404(str(id))

    # Not showing review if it isn't published yet and not viewed by author.
    if review.is_draft and not (current_user.is_authenticated
                                and current_user == review.user):
        raise NotFound("Can't find a review with the specified ID.")
    if review.is_hidden and not current_user.is_admin():
        raise NotFound(gettext("Review has been hidden."))

    revisions = Revision.query.filter_by(review=review)
    count = revisions.count()
    revisions = revisions.order_by(desc(Revision.timestamp)).limit(RESULTS_LIMIT)
    results = list(zip(reversed(range(count-RESULTS_LIMIT, count)), revisions))

    return render_template('review/revisions.html', review=review, results=results, count=count, limit=RESULTS_LIMIT)


@review_bp.route('/<uuid:id>/revisions/more')
def revisions_more(id):
    review = Review.query.get_or_404(str(id))

    # Not showing review if it isn't published yet and not viewed by author.
    if review.is_draft and not (current_user.is_authenticated
                                and current_user == review.user):
        raise NotFound("Can't find a review with the specified ID.")
    if review.is_hidden and not current_user.is_admin():
        raise NotFound(gettext("Review has been hidden."))

    page = int(request.args.get('page', default=0))
    offset = page * RESULTS_LIMIT

    revisions = Revision.query.filter_by(review=review)
    count = revisions.count()
    revisions = revisions.order_by(desc(Revision.timestamp)).offset(offset).limit(RESULTS_LIMIT)
    results = list(zip(reversed(range(count-offset-RESULTS_LIMIT, count-offset)), revisions))

    template = render_template('review/revision_results.html', review=review, results=results, count=count)
    return jsonify(results=template, more=(count-offset-RESULTS_LIMIT) > 0)


@review_bp.route('/write', methods=('GET', 'POST'))
@login_required
def create():
    for entity_type in ENTITY_TYPES:
        entity_id = request.args.get(entity_type)
        if entity_id:
            break

    if not entity_id:
        flash.info(gettext("Please choose an entity to review."))
        return redirect(url_for('search.selector', next=url_for('.create')))

    if current_user.is_blocked:
        flash.error(gettext("You are not allowed to write new reviews because your "
                            "account has been blocked by a moderator."))
        return redirect(url_for('user.reviews', user_id=current_user.id))

    # Checking if the user already wrote a review for this entity
    review = Review.query.filter_by(user=current_user, entity_id=entity_id).first()
    if review:
        flash.error(gettext("You have already published a review for this entity!"))
        return redirect(url_for('review.entity', id=review.id))

    form = ReviewCreateForm(default_language=get_locale())

    if form.validate_on_submit():
        if current_user.is_review_limit_exceeded:
            flash.error(gettext("You have exceeded your limit of reviews per day."))
            return redirect(url_for('user.reviews', user_id=current_user.id))

        is_draft = form.state.data == 'draft'
        review = Review.create(user=current_user, entity_id=entity_id, entity_type=entity_type,
                               text=form.text.data, license_id=form.license_choice.data,
                               language=form.language.data, is_draft=is_draft)
        if is_draft:
            flash.success(gettext("Review has been saved!"))
        else:
            flash.success(gettext("Review has been published!"))
        return redirect(url_for('.entity', id=review.id))

    entity = musicbrainz.get_entity_by_id(entity_id, entity_type)
    if not entity:
        flash.error(gettext("You can only write a review for an entity that exists on MusicBrainz!"))
        return redirect(url_for('search.selector', next=url_for('.create')))

    if entity_type == 'release_group':
        spotify_mappings = mbspotify.mappings(entity_id)
        soundcloud_url = soundcloud.get_url(entity_id)
        return render_template('review/modify/write.html', form=form, entity_type=entity_type, entity=entity, spotify_mappings = spotify_mappings, soundcloud_url=soundcloud_url)
    return render_template('review/modify/write.html', form=form, entity_type=entity_type, entity=entity)


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
    if review.is_hidden and not current_user.is_admin():
        raise NotFound(gettext("Review has been hidden."))

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
        flash.success(gettext("Review has been updated."))
        return redirect(url_for('.entity', id=review.id))
    else:
        form.text.data = review.text
    if review.entity_type == 'release_group':
        spotify_mappings = mbspotify.mappings(review.entity_id)
        soundcloud_url = soundcloud.get_url(review.entity_id)
        return render_template('review/modify/edit.html', form=form, review=review, entity_type=review.entity_type, entity=entity, spotify_mappings = spotify_mappings, soundcloud_url=soundcloud_url)
    return render_template('review/modify/edit.html', form=form, review=review, entity_type=review.entity_type)


@review_bp.route('/<uuid:id>/delete', methods=['GET', 'POST'])
@login_required
def delete(id):
    review = Review.query.get_or_404(str(id))
    if review.user != current_user and not current_user.is_admin():
        raise Unauthorized(gettext("Only the author or an admin can delete this review."))
    if request.method == 'POST':
        review.delete()
        flash.success(gettext("Review has been deleted."))
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
    else:
        vote = None

    review = Review.query.get_or_404(review_id)
    if review.is_hidden and not current_user.is_admin():
        raise NotFound(gettext("Review has been hidden."))
    if review.user == current_user:
        flash.error(gettext("You cannot rate your own review."))
        return redirect(url_for('.entity', id=review_id))
    if current_user.is_vote_limit_exceeded is True and current_user.has_voted(review) is False:
        flash.error(gettext("You have exceeded your limit of votes per day."))
        return redirect(url_for('.entity', id=review_id))
    if current_user.is_blocked:
        flash.error(gettext("You are not allowed to rate this review because "
                            "your account has been blocked by a moderator."))
        return redirect(url_for('.entity', id=review_id))

    db_vote.submit(
        user_id=current_user.id,
        revision_id=review.last_revision.id,
        vote=vote,  # overwrites an existing vote, if needed
    )

    flash.success(gettext("You have rated this review!"))
    return redirect(url_for('.entity', id=review_id))


@review_bp.route('/<uuid:id>/vote/delete', methods=['GET'])
@login_required
def vote_delete(id):
    review = Review.query.get_or_404(str(id))
    if review.is_hidden and not current_user.is_admin():
        raise NotFound(gettext("Review has been hidden."))
    try:
        vote = db_vote.get(user_id=current_user.id, revision_id=review.last_revision.id)
        flash.success(gettext("You have deleted your vote for this review!"))
        db_vote.delete(user_id=vote["user_id"], revision_id=vote["revision_id"])
    except db_exceptions.NoDataFoundException:
        flash.error(gettext("This review is not rated yet."))
    return redirect(url_for('.entity', id=id))


@review_bp.route('/<uuid:id>/report', methods=['GET', 'POST'])
@login_required
def report(id):
    review = Review.query.get_or_404(str(id))
    if review.is_hidden and not current_user.is_admin():
        raise NotFound(gettext("Review has been hidden."))
    if review.user == current_user:
        flash.error(gettext("You cannot report your own review."))
        return redirect(url_for('.entity', id=id))

    if current_user.is_blocked:
        flash.error(gettext("You are not allowed to report this review because "
                            "your account has been blocked by a moderator."))
        return redirect(url_for('.entity', id=id))

    last_revision_id = review.last_revision.id
    count = SpamReport.query.filter_by(user=current_user, revision_id=last_revision_id).count()
    if count > 0:
        flash.error(gettext("You have already reported this review."))
        return redirect(url_for('.entity', id=id))

    form = ReviewReportForm()
    if form.validate_on_submit():
        SpamReport.create(last_revision_id, current_user, form.reason.data)
        flash.success(gettext("Review has been reported."))
        return redirect(url_for('.entity', id=id))

    return render_template('review/report.html', review=review, form=form)


@review_bp.route('/<uuid:id>/hide', methods=['GET', 'POST'])
@login_required
@admin_view
def hide(id):
    review = Review.query.get_or_404(str(id))

    if review.is_hidden:
        flash.info(gettext("Review is already hidden."))
        return redirect(url_for('.entity', id=review.id))

    form = AdminActionForm()
    if form.validate_on_submit():
        review.hide()
        ModerationLog.create(admin_id=current_user.id, action=ACTION_HIDE_REVIEW,
                             reason=form.reason.data, review_id=review.id)
        for report in SpamReport.list(review_id=review.id)[0]:
            report.archive()
        flash.success(gettext("Review has been hidden."))
        return redirect(url_for('.entity', id=review.id))

    return render_template('log/action.html', review=review, form=form, action=ACTION_HIDE_REVIEW)


@review_bp.route('/<uuid:id>/unhide', methods=['POST'])
@login_required
@admin_view
def unhide(id):
    review = Review.query.get_or_404(str(id))
    review.unhide()
    flash.success(gettext("Review is not hidden anymore."))
    return redirect(request.referrer or url_for('user.reviews', user_id=current_user.id))
