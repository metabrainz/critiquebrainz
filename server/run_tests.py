import unittest
import manage
import test_config

if __name__ == '__main__':
    # Creating database-related stuff
    manage.init_postgres(test_config.SQLALCHEMY_DATABASE_URI)

    all = unittest.TestLoader().discover(start_dir='critiquebrainz', pattern='*_test.py')
    unittest.TextTestRunner(verbosity=1).run(all)