from unittest.mock import MagicMock
from critiquebrainz.frontend.testing import FrontendTestCase
import critiquebrainz.db.review as db_review
from critiquebrainz.db.user import User
import critiquebrainz.db.users as db_users
import critiquebrainz.db.license as db_license
import critiquebrainz.frontend.external.musicbrainz_db.release as mb_release
from flask import current_app


def mock_get_entity_by_id(id, type='release_group'):
    if id == '6b3cd75d-7453-39f3-86c4-1441f360e121' and type == 'release_group':
        return {
            'id': '6b3cd75d-7453-39f3-86c4-1441f360e121',
            'title': 'Moderat',
        }
    if id == 'b4e75ef8-3454-4fdc-8af1-61038c856abc' and type == 'event':
        return {
            'id': 'b4e75ef8-3454-4fdc-8af1-61038c856abc',
            'name': 'Rock am Ring 2014',
        }
    if id == 'c5c9c210-b7a0-4f6e-937e-02a586c8e14c' and type == 'place':
        return {
            'id': 'c5c9c210-b7a0-4f6e-937e-02a586c8e14c',
            'name': 'University of London Union',
        }


class ReviewViewsTestCase(FrontendTestCase):

    def setUp(self):
        super(ReviewViewsTestCase, self).setUp()
        self.user = User(db_users.get_or_create("aef06569-098f-4218-a577-b413944d9493", new_user_data={
            "display_name": u"Tester",
        }))
        self.hacker = User(db_users.get_or_create("9371e5c7-5995-4471-a5a9-33481f897f9c", new_user_data={
            "display_name": u"Hacker!",
        }))
        self.license = db_license.create(
            id="CC BY-SA 3.0",
            full_name="Created so we can fill the form correctly.",
        )
        self.review_text = "Testing! This text should be on the page."
        mb_release.browse_releases = MagicMock()
        current_app.jinja_env.filters['entity_details'] = mock_get_entity_by_id

    def create_dummy_review(self, is_draft=False):
        review = db_review.create(
            entity_id="6b3cd75d-7453-39f3-86c4-1441f360e121",
            entity_type="release_group",
            user_id=self.user.id,
            text=self.review_text,
            is_draft=is_draft,
            license_id=self.license["id"],
        )
        return review

    def test_browse(self):
        # Should return 404 if there are no reviews.
        self.assert404(self.client.get("/review/"))

    def test_entity(self):
        review = self.create_dummy_review()
        response = self.client.get("/review/%s" % review["id"])
        self.assert200(response)
        self.assertIn(self.review_text, str(response.data))

    def test_draft_review(self):
        review = self.create_dummy_review(is_draft=True)
        response = self.client.get("/review/%s" % review["id"])
        self.assert404(response, "Drafts shouldn't be publicly visible.")

    def test_missing_review(self):
        response = self.client.get("/review/aef06569-098f-4218-a577-b413944d9493")
        self.assert404(response)

    def test_create(self):
        data = dict(
            release_group="6b3cd75d-7453-39f3-86c4-1441f360e121",
            state='draft',
            text=self.review_text,
            license_choice=self.license["id"],
            language='en',
            agreement='True'
        )

        self.temporary_login(self.user)
        response = self.client.post('/review/write', data=data,
                                    query_string=data, follow_redirects=True)
        self.assert200(response)
        self.assertIn(self.review_text, str(response.data))

    def test_edit(self):
        updated_text = "The text has now been updated"
        data = dict(
            release_group="6b3cd75d-7453-39f3-86c4-1441f360e121",
            state='publish',
            text=updated_text,
            license_choice=self.license["id"],
            language='en',
            agreement='True'
        )

        review = self.create_dummy_review()

        self.temporary_login(self.user)
        response = self.client.post('/review/%s/edit' % review["id"], data=data,
                                    query_string=data, follow_redirects=True)
        self.assert200(response)
        self.assertIn(updated_text, str(response.data))

    def test_delete(self):
        review = self.create_dummy_review()

        self.temporary_login(self.hacker)
        response = self.client.post("/review/%s/delete" % review["id"], follow_redirects=True)
        self.assert401(response, "Only the author can delete this review.")

        self.temporary_login(self.user)
        response = self.client.post("/review/%s/delete" % review["id"], follow_redirects=True)
        self.assert200(response)

    def test_vote_submit_delete(self):
        review = self.create_dummy_review()

        self.temporary_login(self.user)
        response = self.client.post("/review/%s/vote" % review["id"], follow_redirects=True)
        self.assertIn("You cannot rate your own review.", str(response.data))

        self.temporary_login(self.hacker)
        response = self.client.post("/review/%s/vote" % review["id"], data=dict(yes=True),
                                    follow_redirects=True)
        self.assertIn("You have rated this review!", str(response.data))

        response = self.client.get("/review/%s/vote/delete" % review["id"], follow_redirects=True)
        self.assertIn("You have deleted your vote for this review!", str(response.data))

    def test_report(self):
        review = self.create_dummy_review()

        data = dict(reason="Testing reason.")

        self.temporary_login(self.user)
        response = self.client.post("/review/%s/report" % review["id"], follow_redirects=True)
        self.assertIn("You cannot report your own review.", str(response.data))

        self.temporary_login(self.hacker)
        response = self.client.post("/review/%s/report" % review["id"], data=data,
                                    query_string=data, follow_redirects=True)
        self.assertIn("Review has been reported.", str(response.data))

    def test_event_review_pages(self):
        review = db_review.create(
            entity_id="b4e75ef8-3454-4fdc-8af1-61038c856abc",
            entity_type="event",
            user_id=self.user.id,
            text="A great event, enjoyed it.",
            is_draft=False,
            license_id=self.license["id"],
        )

        response = self.client.get("/review/%s" % review["id"])
        self.assert200(response)
        self.assertIn("A great event, enjoyed it.", str(response.data))

    def test_place_review_pages(self):
        review = db_review.create(
            entity_id="c5c9c210-b7a0-4f6e-937e-02a586c8e14c",
            entity_type="place",
            user_id=self.user.id,
            text="A great place.",
            is_draft=False,
            license_id=self.license["id"],
        )

        response = self.client.get("/review/%s" % review["id"])
        self.assert200(response)
        self.assertIn("A great place.", str(response.data))
