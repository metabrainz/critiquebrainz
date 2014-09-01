import unittest
import cache
import random
import string
from frontend import create_app


class CacheTestCase(unittest.TestCase):
    def setUp(self):
        self.app = create_app()

    def test_key_generator(self):
        namespace = 'TEST_NAMESPACE'
        self.app.config['MEMCACHED_NAMESPACE'] = namespace

        with self.app.app_context():
            # Simple key
            self.assertEqual(cache.generate_cache_key('test'), '%s:%s' % (namespace, 'test'))

            # With source
            self.assertEqual(cache.generate_cache_key('test', source='spotify'),
                             '%s:%s:%s' % (namespace, 'spotify', 'test'))

            # With type
            self.assertEqual(cache.generate_cache_key('test', type='user'),
                             '%s:%s:%s' % (namespace, 'user', 'test'))

            # With source and type
            self.assertEqual(cache.generate_cache_key('test', source='spotify', type='user'),
                             '%s:%s:%s:%s' % (namespace, 'spotify', 'user', 'test'))

            # Let's try long keys
            id = ''.join(random.choice(string.lowercase) for x in range(200))
            self.assertLessEqual(len(cache.generate_cache_key(id)), 250)

            id = ''.join(random.choice(string.lowercase) for x in range(249))
            self.assertLessEqual(len(cache.generate_cache_key(id)), 250)

            id = ''.join(random.choice(string.lowercase) for x in range(2000))
            self.assertLessEqual(len(cache.generate_cache_key(id)), 250)

            id = ''.join(random.choice(string.lowercase) for x in range(4000))
            self.assertLessEqual(len(cache.generate_cache_key(id, source='spotify', type='album')), 250)
