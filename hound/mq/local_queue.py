
import Queue

class LocalQueue(object):

    def __new__(cls, *args, **kwargs):

        if not hasattr(cls, '_instance'):
            _instance = super(LocalQueue,cls).__new__(cls, *args, **kwargs)
            setattr(cls, '_instance', _instance)
            _queue = Queue.Queue()
            setattr(_instance, '_queue', _queue)
            return _instance
        else:
            return getattr(cls, '_instance')

    def qsize(self):
        return self._queue.qsize()

    def join(self):
        return self._queue.join()

    def empty(self):
        return self._queue.empty()

    def full(self):
        return self._queue.full()

    def get_nowait(self):
        return self._queue.get_nowait()

    def put_nowait(self,item):
        return self._queue.put_nowait(item)

    def get(self,block=True, timeout=None):
        return self._queue.get(block, timeout)

    def put(self,item, block=True, timeout=None):
        return self._queue.put(item, block, timeout)






