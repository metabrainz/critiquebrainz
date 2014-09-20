import unittest
import utils


class UtilsTestCase(unittest.TestCase):

    def test_generate_string(self):
        length = 42
        str_1 = utils.generate_string(length)
        str_2 = utils.generate_string(length)

        self.assertEqual(len(str_1), length)
        self.assertEqual(len(str_2), length)
        self.assertNotEqual(str_1, str_2)  # Generated strings shouldn't be the same

    def test_validate_uuid(self):
        self.assertTrue(utils.validate_uuid("123e4567-e89b-12d3-a456-426655440000"))
        self.assertFalse(utils.validate_uuid("not-a-uuid"))
