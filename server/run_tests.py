import unittest
from critiquebrainz import create_app
from critiquebrainz.data.manage import init_postgres

if __name__ == '__main__':
    # Creating database-related stuff
    init_postgres(create_app().config['TEST_SQLALCHEMY_DATABASE_URI'])

    all_tests = unittest.TestLoader().discover(start_dir='.', pattern='*_test.py')
    unittest.TextTestRunner(verbosity=1).run(all_tests)