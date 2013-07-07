from .test import *

class PublicationTestCase(AppTestCase):

    def test_show_publication(self):
        response = self.client.get(
            '/publication/%s' % (fixtures.PublicationData.publication01.id))
        self.assert_200(response)
        
        self.assertEqual(response.json['publication']['id'],
                         fixtures.PublicationData.publication01.id)
        response = self.client.get('/publication/%s' % ('not-valid-uuid'))
        self.assert_404(response)
        
        publication = self.db.session.query(models.Publication).\
                           get(fixtures.PublicationData.publication01.id)
        self.db.session.delete(publication)
        self.db.session.commit()
        response = self.client.get(
            '/publication/%s' % (fixtures.PublicationData.publication01.id))
        self.assert_404(response)
