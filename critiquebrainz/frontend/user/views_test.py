from critiquebrainz.frontend.testing import FrontendTestCase
from critiquebrainz.data.model.user import User


class UserViewsTestCase(FrontendTestCase):

    def test_reviews(self):
        user = User.get_or_create(u"aef06569-098f-4218-a577-b413944d9493", u"Tester")
        response = self.client.get("/user/%s" % user.id)
        self.assert200(response)
        self.assertIn("Tester", response.data)

    def test_info(self):
        user = User.get_or_create(u"aef06569-098f-4218-a577-b413944d9493", u"Tester")
        response = self.client.get("/user/%s/info" % user.id)
        self.assert200(response)
        self.assertIn("Tester", response.data)
