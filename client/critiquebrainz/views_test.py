from critiquebrainz.test_case import ClientTestCase


class ViewsTestCase(ClientTestCase):

    def test_404(self):
        response = self.client.get("/404/")
        self.assert404(response)
