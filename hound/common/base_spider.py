from abc import abstractmethod
import six
import uuid
from hound.model.task import Task
from hound.common.exception import *
from hound.mq.local_queue import LocalQueue


class BaseMeta(type):

    def __new__(cls, name, bases, attrs):

        # for k in attrs.keys():
        #     print(str(k) + ' : ' + str(attrs[k]))
        newcls = type.__new__(cls, name, bases, attrs)
        return  newcls

class BaseSpider(object):

    __metaclass__ = BaseMeta
    project_name = None

    def __init__(self):
        self.queue = LocalQueue()

    def crawl(self, url, **kwargs):
        task = Task()

        if kwargs.get('callback'):
            callback = kwargs.get('callback')
            if isinstance(callback, six.string_types) and hasattr(self, callback):
                func = getattr(self, callback)
            elif six.callable(callback) and six.get_method_self(callback) is self:
                func = callback
                task.callback = func.__name__
            else:
                raise NotImplementError()

        task.func = func
        task.url = url
        task.id = str(uuid.uuid4())
        task.spider_cls = self.__class__

        self.queue.put(task)

        # return task

    def on_callback(self, cb_name, response, *args, **kwargs):
        func = getattr(self, cb_name)
        return func(response, *args,**kwargs)





