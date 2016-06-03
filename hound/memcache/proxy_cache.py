import weakref
import random

class ResultCache(object):

    def __new__(cls, *args, **kwargs):

        if not hasattr(cls, '_instance'):
            _instance = super(ResultCache,cls).__new__(cls, *args, **kwargs)
            setattr(cls, '_instance', _instance)
            _cache = weakref.WeakKeyDictionary()
            setattr(_instance, '_cache', _cache)
            return _instance
        else:
            return getattr(cls, '_instance')

    def __init__(self):
        self._cache = []

    def put(self, item):
        self._cache.append(item)

    def get(self):
        return self._cache.pop()

    def get_random(self):
        return self._cache.pop(random.random(0, len(self._cache) - 1))


