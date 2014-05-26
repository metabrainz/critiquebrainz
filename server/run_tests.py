import unittest
import test_config
from critiquebrainz.review.tests import review_test_suite
from critiquebrainz.user.tests import user_test_suite

if __name__ == '__main__':
    # Creating database-related stuff
    import manage
    manage.init_postgres(test_config.SQLALCHEMY_DATABASE_URI)

    # Running tests
    all = unittest.TestSuite([review_test_suite, user_test_suite])
    unittest.TextTestRunner(verbosity=2).run(all)