from tornado import queues

class TornadoQueue(object):

    def __new__(cls, *args, **kwargs):

        if not hasattr(cls, '_instance'):
            _instance = super(TornadoQueue,cls).__new__(cls, *args, **kwargs)
            setattr(cls, '_instance', _instance)
            _queue = queues.Queue()
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

    def get(self, timeout=None):
        return self._queue.get( timeout)

    def put(self,item, timeout=None):
        return self._queue.put(item, timeout)

    def task_done(self):
        return self._queue.task_done()
