from django.test import TestCase, override_settings
from django.core.cache import cache as django_cache

from django_utils import cache


@override_settings(
    CACHES={'default': {
        'BACKEND': 'django.core.cache.backends.locmem.LocMemCache',
        'LOCATION': 'cachetesting'
    }},
    DEFAULT_CACHE_DURATION=30,
)
class CacheUtilsTestCase(TestCase):
    def setUp(self):
        django_cache.clear()
        return super().setUp()

    def test_cachekey(self):
        self.assertEqual(cache.cachekey('testone'), 'testone')
        self.assertEqual(cache.cachekey('test one'), 'test_one')
        self.assertEqual(cache.cachekey(['testone']), 'testone')
        self.assertEqual(cache.cachekey(['test', 'one']), 'testone')
        self.assertEqual(cache.cachekey(['test', 'one', 1]), 'testone1')
        self.assertEqual(cache.cachekey('test', 'one'), 'testone')
        self.assertEqual(cache.cachekey('test', 'one', 1), 'testone1')
        self.assertEqual(cache.cachekey('test', None, 1), 'testNone1')
        self.assertEqual(cache.cachekey(['test', None, 1]), 'testNone1')

    def test_cacheset(self):
        cache.cacheset("testset", 12)
        self.assertEqual(django_cache.get("testset"), 12)
        cache.cacheset(["test", "one two", None, 12], "11")
        self.assertEqual(django_cache.get("testone_twoNone12"), "11")

    async def test_acacheset(self):
        await cache.acacheset("testset1", 12)
        self.assertEqual(django_cache.get("testset1"), 12)
        await cache.acacheset(["test1", "one two", None, 12], "11")
        self.assertEqual(django_cache.get("test1one_twoNone12"), "11")

    def test_cacheget(self):
        django_cache.set("testget", 10, 30)
        self.assertEqual(cache.cacheget("testget", int, 9), 10)
        self.assertEqual(cache.cacheget("testget", str, "9"), "9")
        django_cache.get("testget", "9")
        django_cache.set("testgetNone1", 10, 30)
        self.assertEqual(cache.cacheget(["testget", None, 1], int, 9), 10)
        self.assertEqual(cache.cacheget(["testget", None, 1], str, "9"), "9")
        django_cache.get("testgetNone1", "9")
        django_cache.set("testgetNone2", 10, 30)
        self.assertEqual(cache.cacheget(["testget", None, 2], int,
                                        lambda: 6+3), 10)
        self.assertEqual(cache.cacheget(["testget", None, 2], str,
                                        lambda: str(6+3)), "9")
        django_cache.get("testgetNone2", "9")

    async def test_acacheget(self):
        django_cache.set("testget1", 10, 30)
        self.assertEqual(await cache.acacheget("testget1", int, 9), 10)
        self.assertEqual(await cache.acacheget("testget1", str, "9"), "9")
        django_cache.get("testget1", "9")
        django_cache.set("testget1None1", 10, 30)
        self.assertEqual(await cache.acacheget(["testget1", None, 1], int, 9), 10)
        self.assertEqual(await cache.acacheget(
            ["testget1", None, 1], str, "9"), "9")
        django_cache.get("testget1None1", "9")
        django_cache.set("testget1None2", 10, 30)
        self.assertEqual(await cache.acacheget(["testget1", None, 2], int,
                                        lambda: 6+3), 10)
        self.assertEqual(await cache.acacheget(["testget1", None, 2], str,
                                        lambda: str(6+3)), "9")
        django_cache.get("testget1None2", "9")

    def test_cachedel(self):
        django_cache.set("testdel", 8, 30)
        self.assertEqual(django_cache.get("testdel"), 8)
        cache.cachedel("testdel")
        self.assertEqual(django_cache.get("testdel"), None)
        django_cache.set("testdelNone1", 8, 30)
        self.assertEqual(django_cache.get("testdelNone1"), 8)
        cache.cachedel(["testdel", None, 1])
        self.assertEqual(django_cache.get("testdelNone1"), None)

    async def test_acachedel(self):
        django_cache.set("testdel1", 8, 30)
        self.assertEqual(django_cache.get("testdel1"), 8)
        await cache.acachedel("testdel1")
        self.assertEqual(django_cache.get("testdel1"), None)
        django_cache.set("testdel1None1", 8, 30)
        self.assertEqual(django_cache.get("testdel1None1"), 8)
        await cache.acachedel(["testdel1", None, 1])
        self.assertEqual(django_cache.get("testdel1None1"), None)
