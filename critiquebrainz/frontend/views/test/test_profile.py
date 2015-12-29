from critiquebrainz.frontend.testing import FrontendTestCase
from critiquebrainz.data.model.user import User


class ProfileViewsTestCase(FrontendTestCase):

    def setUp(self):
        super(ProfileViewsTestCase, self).setUp()
        self.user = User.get_or_create(u"Tester", u"aef06569-098f-4218-a577-b413944d9493")

    def test_edit(self):
        data = dict(
            display_name="Some User",
            email='someuser@somesite.com',
            show_gravatar='True'
        )

        response = self.client.post('/profile/edit', data=data,
                                    query_string=data, follow_redirects=True)
        self.assertIn("Please sign in to access this page.", response.data)

        self.temporary_login(self.user)
        response = self.client.post('/profile/edit', data=data,
                                    query_string=data, follow_redirects=True)
        self.assert200(response)
        self.assertIn(data['display_name'], response.data)


    def test_delete(self):
        self.temporary_login(self.user)
        response = self.client.post('/profile/delete', follow_redirects=True)
        self.assert200(response)
