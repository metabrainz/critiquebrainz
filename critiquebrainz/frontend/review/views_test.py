from critiquebrainz.frontend.testing import FrontendTestCase
from critiquebrainz.data.model.review import Review
from critiquebrainz.data.model.user import User
from critiquebrainz.data.model.license import License


class ReviewViewsTestCase(FrontendTestCase):

    def setUp(self):
        super(ReviewViewsTestCase, self).setUp()
        self.user = User.get_or_create(u"Tester", u"aef06569-098f-4218-a577-b413944d9493")
        self.hacker = User.get_or_create(u"Hacker!", u"9371e5c7-5995-4471-a5a9-33481f897f9c")
        self.license = License.create(u"CC BY-SA 3.0", u"Created so we can fill the form correctly.")
        self.review_text = "Testing! This text should be on the page."

    def create_dummy_review(self, is_draft=False):
        review = Review.create(
            release_group="6b3cd75d-7453-39f3-86c4-1441f360e121",
            user=self.user,
            text=self.review_text,
            is_draft=is_draft,
            license_id=self.license.id,
        )
        return review

    def test_review_page(self):
        response = self.client.get("/review/")
        self.assert200(response)

    def test_review_by_uuid_page(self):
        review = self.create_dummy_review()
        response = self.client.get("/review/%s" % review.id)
        self.assert200(response)
        self.assertIn(self.review_text, response.data)

    def test_draft_review_page(self):
        review = self.create_dummy_review(is_draft=True)
        response = self.client.get("/review/%s" % review.id)
        self.assert404(response, "Drafts shouldn't be publicly visible.")

    def test_missing_review_page(self):
        response = self.client.get("/review/aef06569-098f-4218-a577-b413944d9493")
        self.assert404(response)

    def test_write_review_page(self):
        data = dict(
            release_group="6b3cd75d-7453-39f3-86c4-1441f360e121",
            state='draft',
            text=self.review_text,
            license_choice=self.license.id,
            language='en',
            agreement='True'
        )

        self.temporary_login(self.user)
        response = self.client.post('/review/write', data=data,
                                    query_string=data, follow_redirects=True)
        self.assert200(response)
        self.assertIn(self.review_text, response.data)

    def test_edit_review_page(self):
        updated_text = "The text has now been updated"
        data = dict(
            release_group="6b3cd75d-7453-39f3-86c4-1441f360e121",
            state='publish',
            text=updated_text,
            license_choice=self.license.id,
            language='en',
            agreement='True'
        )

        review = self.create_dummy_review()

        self.temporary_login(self.user)
        response = self.client.post('/review/%s/edit' % review.id, data=data,
                                    query_string=data, follow_redirects=True)
        self.assert200(response)
        self.assertIn(updated_text, response.data)

    def test_delete_review_page(self):
        review = self.create_dummy_review()

        self.temporary_login(self.hacker)
        response = self.client.post("/review/%s/delete" % review.id, follow_redirects=True)
        self.assert401(response, "Only the author can delete this review.")

        self.temporary_login(self.user)
        response = self.client.post("/review/%s/delete" % review.id, follow_redirects=True)
        self.assert200(response)

    def test_vote_review_page(self):
        review = self.create_dummy_review()

        self.temporary_login(self.user)
        response = self.client.post("/review/%s/vote" % review.id, follow_redirects=True)
        self.assertIn("You cannot rate your own review.", response.data)

        self.temporary_login(self.hacker)
        response = self.client.post("/review/%s/vote" % review.id, data=dict(yes=True),
                                    follow_redirects=True)
        self.assertIn("You have rated this review!", response.data)

        response = self.client.get("/review/%s/vote/delete" % review.id, follow_redirects=True)
        self.assertIn("You have deleted your vote for this review!", response.data)

    def test_report_review_page(self):
        review = self.create_dummy_review()

        self.temporary_login(self.user)
        response = self.client.post("/review/%s/report" % review.id, follow_redirects=True)
        self.assertFalse(response.json['success'], "Shouldn't be able to report your own reviews.")

        self.temporary_login(self.hacker)
        response = self.client.post("/review/%s/report" % review.id, follow_redirects=True)
        self.assertTrue(response.json['success'])
