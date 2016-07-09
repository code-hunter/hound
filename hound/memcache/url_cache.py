class UrlCache(object):

    def __new__(cls, *args, **kwargs):

        if not hasattr(cls, '_instance'):
            _instance = super(UrlCache,cls).__new__(cls, *args, **kwargs)
            setattr(cls, '_instance', _instance)
            _cache = {}
            setattr(_instance, '_cache', _cache)
            return _instance
        else:
            return getattr(cls, '_instance')

    def is_exists(self, key, value):
        if not self._cache.has_key(key) or  len(self._cache[key]) <= 0:
            return False

        for item in self._cache[key]:
            if value == item:
                return True

        return False

    def put(self, key, value):
        if self._cache.has_key(key):
            if not self.is_url_exists(key, value):
                self._cache[key].append(value)
        else:
            url_list = []
            url_list.append(value)
            self._cache[key] = url_list

    def get(self, key):
        return self._cache.get(key, [])

    def all(self):
        return self._cache
