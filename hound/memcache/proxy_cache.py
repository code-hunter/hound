import random

class ProxyCache(object):

    def __new__(cls, *args, **kwargs):

        if not hasattr(cls, '_instance'):
            _instance = super(ProxyCache,cls).__new__(cls, *args, **kwargs)
            setattr(cls, '_instance', _instance)
            _cache = []
            setattr(_instance, '_cache', _cache)
            return _instance
        else:
            return getattr(cls, '_instance')

    def __init__(self):
        self._cache = []

    def put(self, item):
        '''item format : (host, port)'''
        self._cache.append(item)

    def get(self):
        return self._cache[random.randint(0, len(self._cache) - 1)]


if __name__ == '__main__':

    proxy_cache = ProxyCache()
    proxy_cache.put(('host1', '9090'))
    proxy_cache.put(('host2', '9292'))

    print proxy_cache.get()




