import unittest
from tests import reviews

if __name__ == '__main__':
    suite = unittest.TestLoader().loadTestsFromTestCase(reviews.Reviews)
    unittest.TextTestRunner(verbosity=2).run(suite)