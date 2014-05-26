import unittest
from tests import test_config, reviews

if __name__ == '__main__':
    # Creating database-related stuff
    import manage
    manage.init_postgres(test_config.SQLALCHEMY_DATABASE_URI)

    # Running tests
    suite = unittest.TestLoader().loadTestsFromTestCase(reviews.Reviews)
    unittest.TextTestRunner(verbosity=2).run(suite)