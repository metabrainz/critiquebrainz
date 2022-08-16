from critiquebrainz.frontend.external.bookbrainz_db import author
from critiquebrainz.data.testing import DataTestCase

class AuthorTestCase(DataTestCase):

    def setUp(self):

        super(AuthorTestCase, self).setUp()
        self.bbid1 = "49d873e6-7f3e-4160-9833-5b17d89cf4dc"
        self.bbid2 = "5df290b8-ecd5-44fb-8d05-70e291133688"
        self.bbid3 = "e5c4e68b-bfce-4c77-9ca2-0f0a2d4d09f0"
    
    def test_get_author_by_bbid(self):
        author_info = author.get_author_by_bbid(self.bbid1)
        self.assertEqual(author_info["bbid"], self.bbid1)
        self.assertEqual(author_info["name"], "William Shakespeare")
        self.assertEqual(author_info["sort_name"], "Shakespeare, William")
        self.assertEqual(author_info["author_type"], "Person")
    
    def test_fetch_multiple_authors(self):
        authors = author.fetch_multiple_authors([self.bbid2, self.bbid3])
        self.assertEqual(len(authors), 2)
        self.assertEqual(authors[self.bbid2]["bbid"], self.bbid2)
        self.assertEqual(authors[self.bbid2]["name"], "Charles Dickens")
        self.assertEqual(authors[self.bbid2]["author_type"], "Person")
        self.assertEqual(authors[self.bbid3]["bbid"], self.bbid3)
        self.assertEqual(authors[self.bbid3]["name"], "J. K. Rowling")
        self.assertEqual(authors[self.bbid3]["author_type"], "Person")
