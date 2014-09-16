import unittest
import util


class UtilTestCase(unittest.TestCase):

    def test_slugify(self):
        self.assertEqual(util.slugify(u'CC BY-NC-SA 3.0'), 'cc-by-nc-sa-30')
        self.assertEqual(util.slugify(u'CC BY-SA 3.0'), 'cc-by-sa-30')
