import unittest

if __name__ == '__main__':
    all = unittest.TestLoader().discover(start_dir='critiquebrainz', pattern='*_test.py')
    unittest.TextTestRunner(verbosity=1).run(all)