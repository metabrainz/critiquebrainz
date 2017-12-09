from math import ceil
import logging
from flask import Blueprint, render_template, request, redirect, url_for, jsonify
from flask_babel import gettext, get_locale, lazy_gettext
from flask_login import login_required, current_user
from markdown import markdown
from werkzeug.exceptions import Unauthorized, NotFound, Forbidden, BadRequest
from critiquebrainz.db.review import ENTITY_TYPES
from critiquebrainz.db.moderation_log import ACTION_HIDE_REVIEW
from critiquebrainz.db import vote as db_vote, exceptions as db_exceptions, revision as db_revision
from critiquebrainz.frontend import flash
from critiquebrainz.frontend.external import mbspotify, soundcloud
from critiquebrainz.frontend.forms.log import AdminActionForm
from critiquebrainz.frontend.forms.review import ReviewCreateForm, ReviewEditForm, ReviewReportForm
from critiquebrainz.frontend.login import admin_view
from critiquebrainz.frontend.views import get_avg_rating
from critiquebrainz.utils import side_by_side_diff
import critiquebrainz.db.spam_report as db_spam_report
import critiquebrainz.db.review as db_review
import critiquebrainz.db.moderation_log as db_moderation_log
from critiquebrainz.frontend.external.musicbrainz_db.entities import get_multiple_entities, get_entity_by_id


review_bp = Blueprint('review', __name__)
RESULTS_LIMIT = 10


def get_review_or_404(review_id):
    """Get a review using review ID or raise error 404."""
    try:
        review = db_review.get_by_id(review_id)
    except db_exceptions.NoDataFoundException:
        raise NotFound("Can't find a review with ID: {review_id}".format(review_id=review_id))
    return review


@review_bp.route('/')
def browse():
    entity_type = request.args.get('entity_type', default=None)
    if entity_type == 'all':
        entity_type = None
    page = int(request.args.get('page', default=1))
    if page < 1:
        return redirect(url_for('.browse'))
    limit = 3 * 9  # 9 rows
    offset = (page - 1) * limit
    reviews, count = db_review.list_reviews(sort='created', limit=limit, offset=offset, entity_type=entity_type)
    if not reviews:
        if page - 1 > count / limit:
            return redirect(url_for('review.browse', page=int(ceil(count / limit))))
        else:
            if not entity_type:
                raise NotFound(gettext("No reviews to display."))

    # Loading info about entities for reviews
    entities = [(str(review["entity_id"]), review["entity_type"]) for review in reviews]
    entities_info = get_multiple_entities(entities)

    return render_template('review/browse.html', reviews=reviews, entities=entities_info,
                           page=page, limit=limit, count=count, entity_type=entity_type)


# TODO(psolanki): Refactor this function to remove PyLint warning.
# pylint: disable=too-many-branches
@review_bp.route('/<uuid:id>/revisions/<int:rev>')
@review_bp.route('/<uuid:id>')
def entity(id, rev=None):
    review = get_review_or_404(id)
    # Not showing review if it isn't published yet and not viewed by author.
    if review["is_draft"] and not (current_user.is_authenticated and
                                   current_user == review["user"]):
        raise NotFound(gettext("Can't find a review with the specified ID."))
    if review["is_hidden"]:
        if not current_user.is_admin():
            raise Forbidden(gettext("Review has been hidden. "
                                    "You need to be an administrator to view it."))
        else:
            flash.warn(gettext("Review has been hidden."))

    spotify_mappings = None
    soundcloud_url = None
    if review["entity_type"] == 'release_group':
        spotify_mappings = mbspotify.mappings(str(review["entity_id"]))
        soundcloud_url = soundcloud.get_url(str(review["entity_id"]))
    count = db_revision.get_count(id)
    if not rev:
        rev = count
    if rev < count:
        flash.info(gettext('You are viewing an old revision, the review has been updated since then.'))
    elif rev > count:
        raise NotFound(gettext("The revision you are looking for does not exist."))

    revision = db_revision.get(id, offset=count - rev)[0]
    if not review["is_draft"] and current_user.is_authenticated:  # if user is logged in, get their vote for this review
        try:
            vote = db_vote.get(user_id=current_user.id, revision_id=revision['id'])
        except db_exceptions.NoDataFoundException:
            vote = None
    else:  # otherwise set vote to None, its value will not be used
        vote = None
    if revision["text"] is None:
        review["text_html"] = None
    else:
        review["text_html"] = markdown(revision['text'], safe_mode="escape")

    user_all_reviews, review_count = db_review.list_reviews(  # pylint: disable=unused-variable
        user_id=review["user_id"],
        sort="random",
        exclude=[review["id"]],
    )
    other_reviews = user_all_reviews[:3]
    avg_rating = get_avg_rating(review["entity_id"], review["entity_type"])
    return render_template('review/entity/%s.html' % review["entity_type"], review=review,
                           spotify_mappings=spotify_mappings, soundcloud_url=soundcloud_url,
                           vote=vote, other_reviews=other_reviews, avg_rating=avg_rating)


@review_bp.route('/<uuid:review_id>/revision/<int:revision_id>')
def redirect_to_entity(review_id, revision_id):
    try:
        revision_number = db_revision.get_revision_number(review_id, revision_id)
    except db_exceptions.NoDataFoundException:
        raise NotFound(gettext("The revision you are looking for does not exist."))
    return redirect(url_for('.entity', id=review_id, rev=revision_number))


@review_bp.route('/<uuid:id>/revisions/compare')
def compare(id):
    review = get_review_or_404(id)
    if review["is_draft"] and not (current_user.is_authenticated and
                                   current_user == review["user"]):
        raise NotFound(gettext("Can't find a review with the specified ID."))
    if review["is_hidden"] and not current_user.is_admin():
        raise NotFound(gettext("Review has been hidden."))
    count = db_revision.get_count(id)
    old, new = int(request.args.get('old') or count - 1), int(request.args.get('new') or count)
    if old > count or new > count:
        raise NotFound(gettext("The revision(s) you are looking for does not exist."))
    if old > new:
        return redirect(url_for('.compare', id=id, old=new, new=old))
    left = db_revision.get(id, offset=count - old)[0]
    right = db_revision.get(id, offset=count - new)[0]
    left['number'], right['number'] = old, new
    left['text'], right['text'] = side_by_side_diff(left['text'], right['text'])
    return render_template('review/compare.html', review=review, left=left, right=right)


@review_bp.route('/<uuid:id>/revisions')
def revisions(id):
    review = get_review_or_404(id)
    # Not showing review if it isn't published yet and not viewed by author.
    if review["is_draft"] and not (current_user.is_authenticated and
                                   current_user == review["user"]):
        raise NotFound("Can't find a review with the specified ID.")
    if review["is_hidden"] and not current_user.is_admin():
        raise NotFound(gettext("Review has been hidden."))
    try:
        count = db_revision.get_count(id)
        revisions = db_revision.get(id, limit=RESULTS_LIMIT)
    except db_exceptions.NoDataFoundException:
        raise NotFound(gettext("The revision(s) you are looking for does not exist."))
    votes = db_revision.get_all_votes(id)
    results = list(zip(reversed(range(count - RESULTS_LIMIT, count)), revisions))
    return render_template('review/revisions.html', review=review, results=results,
                           count=count, limit=RESULTS_LIMIT, votes=votes)


@review_bp.route('/<uuid:id>/revisions/more')
def revisions_more(id):
    review = get_review_or_404(id)
    # Not showing review if it isn't published yet and not viewed by author.
    if review["is_draft"] and not (current_user.is_authenticated and
                                   current_user == review["user"]):
        raise NotFound("Can't find a review with the specified ID.")
    if review["is_hidden"] and not current_user.is_admin():
        raise NotFound(gettext("Review has been hidden."))

    page = int(request.args.get('page', default=0))
    offset = page * RESULTS_LIMIT
    try:
        count = db_revision.get_count(id)
        revisions = db_revision.get(id, limit=RESULTS_LIMIT, offset=offset)
    except db_exceptions.NoDataFoundException:
        raise NotFound(gettext("The revision(s) you are looking for does not exist."))
    votes = db_revision.get_all_votes(id)
    results = list(zip(reversed(range(count - offset - RESULTS_LIMIT, count - offset)), revisions))

    template = render_template('review/revision_results.html', review=review, results=results, votes=votes, count=count)
    return jsonify(results=template, more=(count - offset - RESULTS_LIMIT) > 0)


# TODO(psolanki): Refactor this function to remove PyLint warning.
# pylint: disable=too-many-branches
@review_bp.route('/write', methods=('GET', 'POST'))
@login_required
def create():
    entity_id, entity_type = None, None
    for entity_type in ENTITY_TYPES:
        entity_id = request.args.get(entity_type)
        if entity_id:
            entity_type = entity_type
            break

    if not (entity_id or entity_type):
        logging.warning("Unsupported entity type")
        raise BadRequest("Unsupported entity type")

    if not entity_id:
        flash.info(gettext("Please choose an entity to review."))
        return redirect(url_for('search.selector', next=url_for('.create')))

    if current_user.is_blocked:
        flash.error(gettext("You are not allowed to write new reviews because your "
                            "account has been blocked by a moderator."))
        return redirect(url_for('user.reviews', user_id=current_user.id))

    # Checking if the user already wrote a review for this entity
    review = db_review.list_reviews(user_id=current_user.id, entity_id=entity_id)[0]
    if review:
        flash.error(gettext("You have already published a review for this entity!"))
        return redirect(url_for('review.entity', id=review["id"]))

    form = ReviewCreateForm(default_language=get_locale())

    if form.validate_on_submit():
        if current_user.is_review_limit_exceeded:
            flash.error(gettext("You have exceeded your limit of reviews per day."))
            return redirect(url_for('user.reviews', user_id=current_user.id))

        is_draft = form.state.data == 'draft'
        if form.text.data == '':
            form.text.data = None
        review = db_review.create(user_id=current_user.id, entity_id=entity_id, entity_type=entity_type,
                                  text=form.text.data, rating=form.rating.data, license_id=form.license_choice.data,
                                  language=form.language.data, is_draft=is_draft)
        if is_draft:
            flash.success(gettext("Review has been saved!"))
        else:
            flash.success(gettext("Review has been published!"))
        return redirect(url_for('.entity', id=review['id']))

    entity = get_entity_by_id(entity_id, entity_type)
    if not entity:
        flash.error(gettext("You can only write a review for an entity that exists on MusicBrainz!"))
        return redirect(url_for('search.selector', next=url_for('.create')))

    if entity_type == 'release_group':
        spotify_mappings = mbspotify.mappings(entity_id)
        soundcloud_url = soundcloud.get_url(entity_id)
        if not form.errors:
            flash.info(gettext("Please provide some text or a rating for this review."))
        return render_template('review/modify/write.html', form=form, entity_type=entity_type, entity=entity,
                               spotify_mappings=spotify_mappings, soundcloud_url=soundcloud_url)
    if not form.errors:
        flash.info(gettext("Please provide some text or a rating for this review."))
    return render_template('review/modify/write.html', form=form, entity_type=entity_type, entity=entity)


@review_bp.route('/<uuid:id>/edit', methods=('GET', 'POST'))
@login_required
def edit(id):
    review = get_review_or_404(id)
    if review["is_draft"] and current_user != review["user"]:
        raise NotFound(gettext("Can't find a review with the specified ID."))
    if review["user"] != current_user:
        raise Unauthorized(gettext("Only author can edit this review."))
    if review["is_hidden"] and not current_user.is_admin():
        raise NotFound(gettext("Review has been hidden."))

    form = ReviewEditForm(default_license_id=review["license_id"], default_language=review["language"])
    if not review["is_draft"]:
        # Can't change license if review is published.
        del form.license_choice

    if form.validate_on_submit():
        if review["is_draft"]:
            license_choice = form.license_choice.data
        else:
            license_choice = None
        if form.text.data == '':
            form.text.data = None

        try:
            db_review.update(
                review_id=review["id"],
                drafted=review["is_draft"],
                text=form.text.data,
                rating=form.rating.data,
                is_draft=(form.state.data == 'draft'),
                license_id=license_choice,
                language=form.language.data,
            )
        except db_exceptions.BadDataException:
            raise BadRequest(lazy_gettext("Changing license of a published review\
                or converting a published review back to drafts is not allowed."))

        flash.success(gettext("Review has been updated."))
        return redirect(url_for('.entity', id=review["id"]))
    else:
        form.text.data = review["text"]
        form.rating.data = review["rating"]
    if review["entity_type"] == 'release_group':
        spotify_mappings = mbspotify.mappings(str(review["entity_id"]))
        soundcloud_url = soundcloud.get_url(str(review["entity_id"]))
        return render_template('review/modify/edit.html', form=form, review=review, entity_type=review["entity_type"],
                               entity=entity, spotify_mappings=spotify_mappings, soundcloud_url=soundcloud_url)
    return render_template('review/modify/edit.html', form=form, review=review, entity_type=review["entity_type"])


@review_bp.route('/<uuid:id>/delete', methods=['GET', 'POST'])
@login_required
def delete(id):
    review = get_review_or_404(id)
    if review["user"] != current_user and not current_user.is_admin():
        raise Unauthorized(gettext("Only the author or an admin can delete this review."))
    if request.method == 'POST':
        db_review.delete(review["id"])
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

    review = get_review_or_404(review_id)
    if review["is_hidden"] and not current_user.is_admin():
        raise NotFound(gettext("Review has been hidden."))
    if review["user"] == current_user:
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
        revision_id=review["last_revision"]["id"],
        vote=vote,  # overwrites an existing vote, if needed
    )

    flash.success(gettext("You have rated this review!"))
    return redirect(url_for('.entity', id=review_id))


@review_bp.route('/<uuid:id>/vote/delete', methods=['GET'])
@login_required
def vote_delete(id):
    review = get_review_or_404(id)
    if review["is_hidden"] and not current_user.is_admin():
        raise NotFound(gettext("Review has been hidden."))
    try:
        vote = db_vote.get(user_id=current_user.id, revision_id=review["last_revision"]["id"])
        flash.success(gettext("You have deleted your vote for this review!"))
        db_vote.delete(user_id=vote["user_id"], revision_id=vote["revision_id"])
    except db_exceptions.NoDataFoundException:
        flash.error(gettext("This review is not rated yet."))
    return redirect(url_for('.entity', id=id))


@review_bp.route('/<uuid:id>/report', methods=['GET', 'POST'])
@login_required
def report(id):
    review = get_review_or_404(id)
    if review["is_hidden"] and not current_user.is_admin():
        raise NotFound(gettext("Review has been hidden."))
    if review["user"] == current_user:
        flash.error(gettext("You cannot report your own review."))
        return redirect(url_for('.entity', id=id))

    if current_user.is_blocked:
        flash.error(gettext("You are not allowed to report this review because "
                            "your account has been blocked by a moderator."))
        return redirect(url_for('.entity', id=id))

    last_revision_id = review["last_revision"]["id"]
    report = db_spam_report.get(current_user.id, last_revision_id)
    if report:
        flash.error(gettext("You have already reported this review."))
        return redirect(url_for('.entity', id=id))

    form = ReviewReportForm()
    if form.validate_on_submit():
        db_spam_report.create(last_revision_id, current_user.id, form.reason.data)
        flash.success(gettext("Review has been reported."))
        return redirect(url_for('.entity', id=id))

    return render_template('review/report.html', review=review, form=form)


@review_bp.route('/<uuid:id>/hide', methods=['GET', 'POST'])
@login_required
@admin_view
def hide(id):
    review = get_review_or_404(id)
    if review["is_hidden"]:
        flash.info(gettext("Review is already hidden."))
        return redirect(url_for('.entity', id=review["id"]))

    form = AdminActionForm()
    if form.validate_on_submit():
        db_review.set_hidden_state(review["id"], is_hidden=True)
        db_moderation_log.create(admin_id=current_user.id, action=ACTION_HIDE_REVIEW,
                                 reason=form.reason.data, review_id=review["id"])
        review_reports, count = db_spam_report.list_reports(review_id=review["id"])  # pylint: disable=unused-variable
        for report in review_reports:
            db_spam_report.archive(report["user_id"], report["revision_id"])
        flash.success(gettext("Review has been hidden."))
        return redirect(url_for('.entity', id=review["id"]))

    return render_template('log/action.html', review=review, form=form, action=ACTION_HIDE_REVIEW)


@review_bp.route('/<uuid:id>/unhide', methods=['POST'])
@login_required
@admin_view
def unhide(id):
    review = get_review_or_404(id)
    db_review.set_hidden_state(review["id"], is_hidden=False)
    flash.success(gettext("Review is not hidden anymore."))
    return redirect(request.referrer or url_for('user.reviews', user_id=current_user.id))
