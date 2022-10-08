from math import ceil

from brainzutils.musicbrainz_db.exceptions import NoDataFoundException
from flask import Blueprint, render_template, request, redirect, url_for, jsonify
from flask_babel import gettext, get_locale, lazy_gettext
from flask_login import login_required, current_user
from langdetect import detect
from werkzeug.exceptions import Unauthorized, NotFound, Forbidden, BadRequest

import critiquebrainz.db.comment as db_comment
import critiquebrainz.db.moderation_log as db_moderation_log
import critiquebrainz.db.review as db_review
import critiquebrainz.db.spam_report as db_spam_report
import critiquebrainz.db.users as db_users
from critiquebrainz.db import vote as db_vote, exceptions as db_exceptions, revision as db_revision
from critiquebrainz.db.moderation_log import AdminActions
from critiquebrainz.db.review import ENTITY_TYPES
from critiquebrainz.frontend import flash
from critiquebrainz.frontend.external import mbspotify, soundcloud, notify_moderators
from critiquebrainz.frontend.external import mbstore
from critiquebrainz.frontend.forms.comment import CommentEditForm
from critiquebrainz.frontend.forms.log import AdminActionForm
from critiquebrainz.frontend.forms.review import ReviewCreateForm, ReviewEditForm, ReviewReportForm
from critiquebrainz.frontend.login import admin_view
from critiquebrainz.frontend.views import get_avg_rating
from critiquebrainz.frontend.views import markdown
from critiquebrainz.utils import side_by_side_diff

review_bp = Blueprint('review', __name__)
RESULTS_LIMIT = 10


def get_review_or_404(review_id):
    """Get a review using review ID or raise error 404."""
    try:
        review = db_review.get_by_id(review_id)
    except db_exceptions.NoDataFoundException:
        raise NotFound(gettext("Can't find a review with ID: %(review_id)s!", review_id=review_id))
    return review


valid_browse_sort = ['published_on', 'popularity']
valid_browse_sort_order = ['asc', 'desc']
valid_entity_types = ENTITY_TYPES + ['musicbrainz', 'bookbrainz']

@review_bp.route('/')
def browse():
    entity_type = request.args.get('entity_type', default=None)
    sort = request.args.get('sort', default='published_on')
    sort_order = request.args.get('sort_order', default='desc')
    if entity_type == 'all':
        entity_type = None

    sort_options = {
        ('popularity', 'asc'): gettext('Least Popular'),
        ('popularity', 'desc'): gettext('Most Popular'),
        ('published_on', 'desc'): gettext('Newest'),
        ('published_on', 'asc'): gettext('Oldest')
    }

    if entity_type and entity_type not in valid_entity_types:
        raise BadRequest("Not a valid entity type.")

    if sort not in valid_browse_sort:
        raise BadRequest("Not a valid sort field.")

    if sort_order not in valid_browse_sort_order:
        raise BadRequest("Not a valid sort order.")

    try:
        page = int(request.args.get('page', default=1))
    except ValueError:
        raise BadRequest("Invalid page number!")
    
    if page < 1:
        return redirect(url_for('.browse'))
    limit = 3 * 9  # 9 rows
    offset = (page - 1) * limit
    reviews, count = db_review.list_reviews(sort=sort, sort_order=sort_order, limit=limit, offset=offset, entity_type=entity_type)
    if not reviews:
        if page - 1 > count / limit:
            return redirect(url_for('review.browse', page=int(ceil(count / limit))))

        if not entity_type:
            raise NotFound(gettext("No reviews to display."))

    # Loading info about entities for reviews
    entities = [(str(review["entity_id"]), review["entity_type"]) for review in reviews]
    entities_info = mbstore.get_multiple_entities(entities)

    # If we don't have metadata for a review, remove it from the list
    # This will have the effect of removing an item from the 3x9 grid of reviews, but it
    # happens so infrequently that we don't bother to back-fill it.
    retrieved_entity_mbids = entities_info.keys()
    reviews = [r for r in reviews if str(r["entity_id"]) in retrieved_entity_mbids]

    return render_template('review/browse.html', reviews=reviews, entities=entities_info,
                           page=page, limit=limit, count=count, entity_type=entity_type, sort=sort, sort_order=sort_order, sort_options=sort_options)


# TODO(psolanki): Refactor this function to remove PyLint warning.
# pylint: disable=too-many-branches

def get_entity_title(_entity):
    title = None
    if 'title' in _entity:
        title = _entity['title']
    elif 'name' in _entity:
        title = _entity['name']
    return title


@review_bp.route('/<uuid:id>/revisions/<int:rev>')
@review_bp.route('/<uuid:id>')
def entity(id, rev=None):
    review = get_review_or_404(id)
    # Not showing review if it isn't published yet and not viewed by author.
    if review["is_draft"] and not (current_user.is_authenticated and
                                   current_user == review["user"]):
        raise NotFound(gettext("Can't find a review with the specified ID."))

    if review["is_hidden"]:
        # show review to admin users with a warning that it is hidden
        if current_user.is_admin():
            flash.warn(gettext("Review has been hidden."))
        elif current_user.is_authenticated and current_user == review["user"]:
            # show to the author of the review that it was hidden but not the actual review
            raise Forbidden(gettext("Review has been hidden. "
                                    "You need to be an administrator to view it."))
        else:
            # for all other users, return a 404 as if the review didn't exist
            raise NotFound(gettext("Can't find a review with ID: %(review_id)s!", review_id=id))

    spotify_mappings = None
    soundcloud_url = None
    if review["entity_type"] == 'release_group':
        spotify_mappings = mbspotify.mappings(str(review["entity_id"]))
        soundcloud_url = soundcloud.get_url(str(review["entity_id"]))

    entity = mbstore.get_entity_by_id(review["entity_id"], review["entity_type"])
    if not entity:
        raise NotFound("This review is for an item that doesn't exist")

    count = db_revision.get_count(id)
    if not rev:
        rev = count
    if rev < count:
        flash.info(gettext('You are viewing an old revision, the review has been updated since then.'))
    elif rev > count:
        raise NotFound(gettext("The revision you are looking for does not exist."))

    revision = db_revision.get(id, offset=count - rev)[0]
    if not review["is_draft"] and current_user.is_authenticated:
        # if user is logged in, get their vote for this review
        try:
            vote = db_vote.get(user_id=current_user.id, revision_id=revision['id'])
        except db_exceptions.NoDataFoundException:
            vote = None
    else:  # otherwise set vote to None, its value will not be used
        vote = None
    if revision["text"] is None:
        review["text_html"] = None
    else:
        review["text_html"] = markdown.format_markdown_as_safe_html(revision['text'])

    review["rating"] = revision["rating"]

    user_all_reviews, _ = db_review.list_reviews(
        user_id=review["user_id"],
        sort="random",
        exclude=[review["id"]],
    )
    other_reviews = user_all_reviews[:3]
    avg_rating = get_avg_rating(review["entity_id"], review["entity_type"])

    comments, count = db_comment.list_comments(review_id=id)
    for comment in comments:
        comment["text_html"] = markdown.format_markdown_as_safe_html(comment["last_revision"]["text"])
    comment_form = CommentEditForm(review_id=id)
    return render_template('review/entity/%s.html' % review["entity_type"], review=review,
                           spotify_mappings=spotify_mappings, soundcloud_url=soundcloud_url,
                           vote=vote, other_reviews=other_reviews, avg_rating=avg_rating,
                           comment_count=count, comments=comments, comment_form=comment_form,
                           entity=entity)


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
    entity = mbstore.get_entity_by_id(review["entity_id"], review["entity_type"])
    if not entity:
        raise NotFound("This review is for an item that doesn't exist")

    if review["is_draft"] and not (current_user.is_authenticated and
                                   current_user == review["user"]):
        raise NotFound(gettext("Can't find a review with the specified ID."))
    if review["is_hidden"] and not current_user.is_admin():
        raise NotFound(gettext("Review has been hidden."))
    count = db_revision.get_count(id)

    try:
        old = int(request.args.get('old', default=count - 1))
    except ValueError:
        raise BadRequest("Invalid old revision number!")
    
    try:
        new = int(request.args.get('new', count))
    except ValueError:
        raise BadRequest("Invalid new revision number!")

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
    entity = mbstore.get_entity_by_id(review["entity_id"], review["entity_type"])
    if not entity:
        raise NotFound("This review is for an item that doesn't exist")

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
    entity = mbstore.get_entity_by_id(review["entity_id"], review["entity_type"])
    if not entity:
        raise NotFound("This review is for an item that doesn't exist")

    # Not showing review if it isn't published yet and not viewed by author.
    if review["is_draft"] and not (current_user.is_authenticated and
                                   current_user == review["user"]):
        raise NotFound("Can't find a review with the specified ID.")
    if review["is_hidden"] and not current_user.is_admin():
        raise NotFound(gettext("Review has been hidden."))

    try:
        page = int(request.args.get('page', default=0))
    except ValueError:
        raise BadRequest("Invalid page number!")
    
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


@review_bp.route('/write/<entity_type>/<entity_id>/', methods=('GET', 'POST'))
@review_bp.route('/write/')
@login_required
def create(entity_type=None, entity_id=None):
    if not (entity_id or entity_type):
        for allowed_type in ENTITY_TYPES:
            if mbid := request.args.get(allowed_type):
                entity_type = allowed_type
                entity_id = mbid
                break

        if entity_type:
            return redirect(url_for('.create', entity_type=entity_type, entity_id=entity_id))

        flash.info(gettext("Please choose an entity to review."))
        return redirect(url_for('search.index'))

    if entity_type not in ENTITY_TYPES:
        raise BadRequest("You can't write reviews about this type of entity.")

    if current_user.is_blocked:
        flash.error(gettext("You are not allowed to write new reviews because your "
                            "account has been blocked by a moderator."))
        return redirect(url_for('user.reviews', user_ref=current_user.user_ref))

    # Checking if the user already wrote a review for this entity
    reviews, count = db_review.list_reviews(user_id=current_user.id, entity_id=entity_id, inc_drafts=True, inc_hidden=True)
    review = reviews[0] if count != 0 else None

    if review:
        if review['is_draft']:
            return redirect(url_for('review.edit', id=review['id']))
        elif review['is_hidden']:
            return redirect(url_for('review.entity', id=review['id']))
        else:
            flash.error(gettext("You have already published a review for this entity"))
            return redirect(url_for('review.entity', id=review["id"]))

    if current_user.is_review_limit_exceeded:
        flash.error(gettext("You have exceeded your limit of reviews per day."))
        return redirect(url_for('user.reviews', user_ref=current_user.user_ref))

    form = ReviewCreateForm(default_language=get_locale())

    if form.validate_on_submit():
        is_draft = form.state.data == 'draft'
        if form.text.data == '':
            form.text.data = None
        review = db_review.create(user_id=current_user.id, entity_id=entity_id, entity_type=entity_type,
                                  text=form.text.data, rating=form.rating.data,
                                  language=form.language.data, is_draft=is_draft)
        if is_draft:
            flash.success(gettext("Review has been saved!"))
        else:
            flash.success(gettext("Review has been published!"))
        return redirect(url_for('.entity', id=review['id']))

    _entity = mbstore.get_entity_by_id(entity_id, entity_type)
    data = {
        "form": form,
        "entity_type": entity_type,
        "entity": _entity,
    }
    if not _entity:
        flash.error(gettext("You can only write a review for an entity that exists on MusicBrainz!"))
        return redirect(url_for('search.index'))

    data["entity_title"] = get_entity_title(_entity)
    if entity_type == "release_group":
        data["spotify_mappings"] = mbspotify.mappings(entity_id)
        data["soundcloud_url"] = soundcloud.get_url(entity_id)

    if not form.errors:
        flash.info(gettext("Please provide some text or a rating for this review."))
    return render_template('review/modify/write.html', **data)


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
    data = {
        "form": form,
        "entity_type": review["entity_type"],
        "review": review,
    }

    # The purpose of the check is to not create unnecessary revisions. So updating a draft review
    # without changes or editing a published review without changes is not allowed. But publishing
    # a draft review without changes is allowed.
    if form.state.data == "draft" and review["is_draft"] \
            and form.text.data == review["text"] and form.rating.data == review["rating"]:
        form.form_errors.append("You must edit either text or rating to update the draft.")
    elif not review["is_draft"] and form.text.data == review["text"] \
            and form.rating.data == review["rating"]:
        form.form_errors.append("You must edit either text or rating to update the review.")
    elif form.validate_on_submit():
        if review["is_draft"]:
            license_choice = db_review.DEFAULT_LICENSE_ID
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
        data["spotify_mappings"] = mbspotify.mappings(str(review["entity_id"]))
        data["soundcloud_url"] = soundcloud.get_url(str(review["entity_id"]))

    _entity = mbstore.get_entity_by_id(review["entity_id"], review["entity_type"])
    data["entity_title"] = get_entity_title(_entity)
    data["entity"] = _entity
    return render_template('review/modify/edit.html', **data)


@review_bp.route('/write/get_language', methods=['POST'])
@login_required
def get_language():
    """Return the most likely language of the text."""
    return detect(request.form['text'])


@review_bp.route('/<uuid:id>/delete', methods=['GET', 'POST'])
@login_required
def delete(id):
    review = get_review_or_404(id)
    if review["user"] != current_user and not current_user.is_admin():
        raise Unauthorized(gettext("Only the author or an admin can delete this review."))
    if request.method == 'POST':
        db_review.delete(review["id"])
        flash.success(gettext("Review has been deleted."))
        return redirect(url_for('user.reviews', user_ref=current_user.user_ref))
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
    if current_user.is_vote_limit_exceeded and not db_users.has_voted(current_user.id, review_id):
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
        notify_moderators.mail_review_report(
            user=current_user,
            reason=form.reason.data,
            review=review,
        )
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
        db_moderation_log.create(admin_id=current_user.id, action=AdminActions.ACTION_HIDE_REVIEW,
                                 reason=form.reason.data, review_id=review["id"])
        review_reports, count = db_spam_report.list_reports(review_id=review["id"])  # pylint: disable=unused-variable
        for report in review_reports:
            db_spam_report.archive(report["user_id"], report["revision_id"])
        return redirect(url_for('.entity', id=review["id"]))

    return render_template('log/action.html', review=review, form=form, action=AdminActions.ACTION_HIDE_REVIEW.value)


@review_bp.route('/<uuid:id>/unhide', methods=['GET', 'POST'])
@login_required
@admin_view
def unhide(id):
    review = get_review_or_404(id)
    if not review["is_hidden"]:
        flash.info(gettext("Review is not hidden."))
        return redirect(url_for('.entity', id=review["id"]))

    form = AdminActionForm()
    if form.validate_on_submit():
        db_review.set_hidden_state(review["id"], is_hidden=False)
        db_moderation_log.create(admin_id=current_user.id, action=AdminActions.ACTION_UNHIDE_REVIEW,
                                 reason=form.reason.data, review_id=review["id"])
        flash.success(gettext("Review is not hidden anymore."))
        return redirect(url_for('.entity', id=review["id"]))

    return render_template('log/action.html', review=review, form=form, action=AdminActions.ACTION_UNHIDE_REVIEW.value)
