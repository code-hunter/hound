from abc import abstractmethod
import six
import uuid
from hound.model.task import Task
from hound.common.exception import *
from hound.mq.local_queue import LocalQueue
from hound.db.es import ESClient
from hound.db import get_db_client


class BaseMeta(type):

    def __new__(cls, name, bases, attrs):

        for k in attrs.keys():
            print(str(k) + ' : ' + str(attrs[k]))

        newcls = type.__new__(cls, name, bases, attrs)
        return  newcls

class BaseSpider(object):

    __metaclass__ = BaseMeta
    project_name = None
    db_conn = None

    def __init__(self):
        self.queue = LocalQueue()

    def create_task(self, url, **kwargs):
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

        if kwargs.get('db_conn'):
            task.db_conn =  kwargs.get('db_conn')
        elif getattr(self, 'db_conn'):
            task.db_conn = getattr(self, 'db_conn')

        task.request_params = {}
        if kwargs.get('headers'):
            task.request_params['headers'] = kwargs.get('headers', None)
        if kwargs.get('proxy_host'):
            task.request_params['proxy_host'] = kwargs.get('proxy_host')
        if kwargs.get('proxy_port'):
            task.request_params['proxy_port'] = kwargs.get('proxy_port')

        task.func = func
        task.url = url
        task.id = str(uuid.uuid4())
        task.spider_cls = self.__class__

        self.queue.put(task)

    def crawl(self, urls, **kwargs):

        if isinstance(urls, list):
            for url in urls:
                self.create_task(url, **kwargs)
        elif isinstance(urls, str):
            self.create_task(urls, **kwargs)
        elif isinstance(urls, unicode):
            self.create_task(urls, **kwargs)
        else:
            raise InvalidUrl


    def on_callback(self, cb_name, response, *args, **kwargs):
        func = getattr(self, cb_name)
        return func(response, *args, **kwargs)

    def on_save(self, task, result):

        if not task.db_conn:
            raise NoTaskDBConnSpecified

        db_client = get_db_client(task.db_conn)

        if isinstance(result, dict):
            db_client.create(result)
        elif isinstance(result, list):
            for item in result:
                db_client.create(item)
        else:
            raise InvalidResult









