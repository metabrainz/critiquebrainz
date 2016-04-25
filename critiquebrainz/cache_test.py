import unittest
import datetime
from critiquebrainz import cache
from pymemcache.client.hash import HashClient


class CacheTestCase(unittest.TestCase):
    """Testing our custom wrapper for memcached."""

    def setUp(self):
        self.servers = [("127.0.0.1", 11211)]
        self.namespace = "CB_TEST"
        cache.init(
            servers=self.servers,
            namespace=self.namespace,
        )
        # Making sure there are no items in cache before we run each test
        cache.flush_all()
        print(cache._mc)

    def test_single(self):
        self.assertTrue(cache.set("test2", "Hello!"))
        self.assertEqual(cache.get("test2"), "Hello!")

    def test_single_with_namespace(self):
        self.assertTrue(cache.set("test", 42, namespace="testing"))
        self.assertEqual(cache.get("test", namespace="testing"), 42)

    def test_single_fancy(self):
        self.assertTrue(cache.set("test3", "Привет!"))
        self.assertEqual(cache.get("test3"), "Привет!")

    def test_single_dict(self):
        dictionary = {
            "fancy": "yeah",
            "wow": 11,
        }
        cache.set('some_dict', dictionary)
        self.assertEqual(cache.get('some_dict'), dictionary)

    def test_single_dict_fancy(self):
        dictionary = {
            "fancy": "Да",
            "тест": 11,
        }
        cache.set('some_dict', dictionary)
        self.assertEqual(cache.get('some_dict'), dictionary)

    def test_datetime(self):
        self.assertTrue(cache.set('some_time', datetime.datetime.now()))
        self.assertEqual(type(cache.get('some_time')), datetime.datetime)

        dictionary = {
            "id": 1,
            "created": datetime.datetime.now(),
        }
        self.assertTrue(cache.set('some_other_time', dictionary))
        self.assertEqual(cache.get('some_other_time'), dictionary)

    def test_delete(self):
        key = "testing"
        self.assertTrue(cache.set(key, "Пример"))
        self.assertEqual(cache.get(key), "Пример")
        self.assertTrue(cache.delete(key))
        self.assertIsNone(cache.get(key))

    def test_delete_with_namespace(self):
        key = "testing"
        namespace = "spaaaaaaace"
        self.assertTrue(cache.set(key, "Пример", namespace=namespace))
        self.assertEqual(cache.get(key, namespace=namespace), "Пример")
        self.assertTrue(cache.delete(key, namespace=namespace))
        self.assertIsNone(cache.get(key, namespace=namespace))

    def test_many(self):
        # With namespace
        mapping = {
            "test1": "Hello",
            "test2": "there",
        }
        self.assertTrue(cache.set_many(mapping, namespace="testing!"))
        self.assertEqual(cache.get_many(mapping.keys(), namespace="testing!"), mapping)

        # Without a namespace
        mapping = {
            "test1": "What's",
            "test2": "good",
        }
        self.assertTrue(cache.set_many(mapping))
        self.assertEqual(cache.get_many(mapping.keys()), mapping)

    def test_invalidate_namespace(self):
        namespace = "test"
        self.assertTrue(cache.invalidate_namespace(namespace))
        self.assertTrue(cache.invalidate_namespace(namespace))


class CacheBaseTestCase(unittest.TestCase):
    """Testing underlying library."""

    def setUp(self):
        self.servers = [("127.0.0.1", 11211)]
        self.client = HashClient(self.servers)

        # Making sure there are no items in cache before we run each test
        self.client.flush_all()

    def test_single(self):
        self.client.set('some_key', 'some value')
        result = self.client.get('some_key')
        self.assertEqual(result, b'some value')

    def test_single_int(self):
        # Note that it returns bytes even if you put an integer inside
        self.client.set('some_int', 42)
        result = self.client.get('some_int')
        self.assertEqual(result, b'42')

    def test_single_fancy(self):
        self.client.set('some_key', 'Пример'.encode(cache.CONTENT_ENCODING))
        result = self.client.get('some_key')
        self.assertEqual(result, 'Пример'.encode(cache.CONTENT_ENCODING))

    def test_single_dict(self):
        self.client.set('some_dict', {
            "fancy": "yeah",
            "wow": 11,
        })
        result = self.client.get('some_dict')
        self.assertTrue(result == b"{'wow': 11, 'fancy': 'yeah'}" or
                        result == b"{'fancy': 'yeah', 'wow': 11}")

    def test_increment(self):
        key = "key_for_testing"

        # Initially nothing
        self.assertIsNone(self.client.incr(key, 1))
        self.assertEqual(self.client.get(key), None)

        self.assertTrue(self.client.set(key, 1))
        self.assertEqual(self.client.get(key), b'1')
        self.assertTrue(self.client.incr(key, 1))
        self.assertEqual(self.client.get(key), b'2')
        self.assertTrue(self.client.incr(key, 2))
        self.assertEqual(self.client.get(key), b'4')


