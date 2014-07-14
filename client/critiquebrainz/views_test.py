from critiquebrainz.test_case import ClientTestCase


class ViewsTestCase(ClientTestCase):

    def test_index_handler(self):
        response = self.client.get("/")
        self.assert200(response)

    def test_about_page(self):
        response = self.client.get("/about/")
        self.assert200(response)

    def test_404(self):
        response = self.client.get("/404/")
        self.assert404(response)
