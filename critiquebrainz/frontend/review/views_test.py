from critiquebrainz.frontend.testing import FrontendTestCase
from critiquebrainz.data.model.review import Review
from critiquebrainz.data.model.user import User
from critiquebrainz.data.model.license import License


class ReviewViewsTestCase(FrontendTestCase):

    def setUp(self):
        super(ReviewViewsTestCase, self).setUp()
        self.user = User.get_or_create(u"aef06569-098f-4218-a577-b413944d9493", u"Tester")
        self.license = License.create(u"Test", u"Test License")

    def test_review_page(self):
        text = "Testing! This text should be on the page."
        review = Review.create(
            release_group="6b3cd75d-7453-39f3-86c4-1441f360e121",
            user=self.user,
            text=text,
            is_draft=False,
            license_id=self.license.id,
        )
        response = self.client.get("/review/%s" % review.id)
        self.assert200(response)
        self.assertIn(text, response.data)

    def test_draft_review_page(self):
        review = Review.create(
            release_group="885181a4-9133-485f-bfce-fddc1168a3c1",
            user=self.user,
            text=u"Testing!",
            is_draft=True,
            license_id=self.license.id,
        )
        response = self.client.get("/review/%s" % review.id)
        self.assert404(response, "Drafts shouldn't be publicly visible.")

    def test_missing_review_page(self):
        response = self.client.get("/review/aef06569-098f-4218-a577-b413944d9493")
        self.assert404(response)
