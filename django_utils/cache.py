"""
Cache related common utils.
"""

from string import ascii_letters, digits
import logging
import inspect

from django.conf import settings
from django.core.cache import cache
from django.db.models import QuerySet


LOG_TAG = "cache"
safechars = ''.join([ascii_letters, digits, '_-'])

def cachekey(*args):
    """Converts and concatenates arguments to use them as cache key."""
    if len(args) == 1 and isinstance(args[0], (list, tuple)):
        args = args[0]
    key = ''.join([''.join([char if char in safechars else str(ord(char))
                            for char in val.replace(' ', '_')])
                   for val in [val if isinstance(val, (bytes, str)) else str(val)
                               for val in args]])
    if len(key) > 250:
        key = key.replace('_', '')
    return key if len(key) <= 250 else key[:250]

def cacheset(
    key, value=None,
    duration=getattr(settings, 'DEFAULT_CACHE_DURATION', 604800)
):
    """Caches a value.

    :param key: Cache key.
    :param value: The value to cache.
    :param duration: Cache expiration period in seconds or None.
    
    """
    params = [cachekey(*key if isinstance(key, (tuple, list)) else key), value]
    if isinstance(duration, int):
        params.append(duration)
    try:
        cache.set(*params)
    except Exception as err:
        logging.getLogger(LOG_TAG).exception(
            'Error on value caching for {0}: {1}'.format(repr(params), repr(err)
        ))

async def acacheset(
    key, value=None,
    duration=getattr(settings, 'DEFAULT_CACHE_DURATION', 604800)
):
    """Caches a value. Asynchronous version.

    :param key: Cache key.
    :param value: The value to cache.
    :param duration: Cache expiration period in seconds or None.
    
    """
    params = [cachekey(*key if isinstance(key, (tuple, list)) else key), value]
    if isinstance(duration, int):
        params.append(duration)
    try:
        await cache.aset(*params)
    except Exception as err:
        logging.getLogger(LOG_TAG).exception(
            'Error on value caching for {0}: {1}'.format(repr(params), repr(err)
        ))

def cacheget(
        key, cls=None, default=None,
        duration=getattr(settings, 'DEFAULT_CACHE_DURATION', 604800)
):
    """
    Triest to get cached value. Caches and returns the default value on
    failure.

    :param key: Cache key.
    :param cls: Class for result validation. May be a tuple, a list, or a model.
    :param default: Default value or lambda for calculation.
    :param duration: Cache expiration period in seconds or None.
    :returns: Cached or default value.
    
    """
    result = cache.get(cachekey(*key if isinstance(key, (tuple, list)) else key))
    if (isinstance(result, cls) or \
        (isinstance(result, QuerySet) and result.model == cls) or \
        (isinstance(result, (list, tuple)) and len(result)
            and isinstance(result[0], cls))
    ):
        return result
    if default is not None:
        if callable(default):
            default = default()
        cacheset(key, value=default, duration=duration)
        return default
    return None

async def acacheget(
        key, cls=None, default=None,
        duration=getattr(settings, 'DEFAULT_CACHE_DURATION', 604800)
):
    """
    Triest to get cached value. Caches and returns the default value on
    failure. Asynchronous version.

    :param key: Cache key.
    :param cls: Class for result validation. May be a tuple, a list, or a model.
    :param default: Default value or lambda for calculation.
    :param duration: Cache expiration period in seconds or None.
    :returns: Cached or default value.
    
    """
    result = await cache.aget(
        cachekey(*key if isinstance(key, (list, tuple)) else key))
    if (isinstance(result, cls) or \
        (isinstance(result, QuerySet) and result.model == cls) or \
        (isinstance(result, (list, tuple)) and len(result)
            and isinstance(result[0], cls))
    ):
        return result
    if default is not None:
        if callable(default):
            if inspect.iscoroutinefunction(default):
                default = await default()
            else:
                default = default()
        await acacheset(key, value=default, duration=duration)
        return default
    return None

def cachedel(key):
    """Clears a cached value.

    :param key: Cache key.
    
    """
    cacheset(key, None, 1)
    cache.delete(cachekey(*key if isinstance(key, (tuple, list)) else key))

async def acachedel(key):
    """Clears a cached value. Asynchronous version.

    :param key: Cache key.
    
    """
    await acacheset(key, None, 1)
    await cache.adelete(cachekey(*key if isinstance(key, (tuple, list)) else key))