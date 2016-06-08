import weakref

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

    def put(self, key, value):
        self._cache[key] = value

    def get(self, key):
        return self._cache[key]

    def all(self):
        return self._cache

