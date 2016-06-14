from abc import abstractmethod
import six
import uuid
from hound.model.task import Task
from hound.model.task_chain import TaskChain
from hound.model.archive import Archive
from hound.model.entry import Entry
from hound.common.exception import *
from hound.common.md5 import getMd5
from hound.db import get_db_client
from hound.mq import get_mq
from hound.memcache.result_cache import ResultCache


class BaseMeta(type):

    def __new__(cls, name, bases, attrs):

        newcls = type.__new__(cls, name, bases, attrs)
        return  newcls

class BaseSpider(object):

    __metaclass__ = BaseMeta
    project_name = None
    db_conn = None
    _stop = False

    def __init__(self):
        self.queue = get_mq()
        self.result_cache = ResultCache()

    def _create_task(self, url, **kwargs):
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
        task.cached = kwargs.get('cached', False)
        task.id = str(uuid.uuid4())
        task.spider_cls = self.__class__

        return task

    def create_task(self, url, **kwargs):
        task = self._create_task(url, **kwargs)
        self.queue.put(task)

    def create_task_chain(self, urls, **kwargs):
        task_chain = TaskChain()

        for url in urls:
            task_chain.put(self._create_task(url, **kwargs))

        self.queue.put(task_chain)

    def crawl(self, urls, **kwargs):

        if self._stop:
            return None

        if isinstance(urls, list):
            if len(urls) == 1:
                self.create_task(urls, **kwargs)
            else:
                self.create_task_chain(urls, **kwargs)
        elif isinstance(urls, str):
            self.create_task(urls, **kwargs)
        elif isinstance(urls, unicode):
            self.create_task(urls, **kwargs)
        else:
            raise InvalidUrl


    def on_callback(self, cb_name, response, *args, **kwargs):
        func = getattr(self, cb_name)
        return func(response, *args, **kwargs)

    def on_cache(self, task, result):

        def _cache(task, item):
            entry = Entry()
            entry.url = task.url
            entry.md5 = getMd5(task.url)
            entry.last_archive = item
            entry.last_fetched_time = task.end_time

            self.result_cache.put(entry.md5, entry)

        if isinstance(result, list):
            if len(result) <= 0:
                raise NoResultError

            last_cached_archive = result[0]
            if not isinstance(last_cached_archive, Archive):
                raise InvalidCachedType

            _cache(task, last_cached_archive)

        elif isinstance(result, Archive):
            _cache(task, result)

        else:
            raise InvalidCachedType

    def on_save(self, task, result):

        if not task.db_conn:
            raise NoTaskDBConnSpecified

        db_client = get_db_client(task.db_conn)

        if isinstance(result, dict):
            db_client.create(result)
        elif isinstance(result, Archive):
            db_client.client(result.as_dict())
        elif isinstance(result, list):
            for item in result:
                db_client.create(item)
        else:
            raise InvalidResult

    def check_result(self, task, result):
        '''if item has been cached, drop results after the item, and set stop_spider'''
        found = False
        cached_key = getMd5(task.url)
        cached_item = self.result_cache.get(cached_key)

        if not cached_item:
            return (result, found)

        last_cache_archive = cached_item.last_archive

        index = 0
        if isinstance(result, list):
            for item in result:
                if item.md5 == last_cache_archive.md5:
                    found = True
                    break
                index += 1
            if found:
                return ( None  if index == 0 else  result[:index], found)

        elif isinstance(result, Archive):
            if result.md5 == cached_item.md5:
                found = True
            if found:
                return (None, found)
        elif isinstance(result, dict):
            if result['md5'] == cached_item.md5:
                found = True
            if found:
                return (None, found)
        else:
            raise InvalidResult

        return (result, found)

    @classmethod
    def stop_spider(cls):
        '''set flag to stop spider'''
        cls._stop = True

    @classmethod
    def start_spider(cls):
        cls._stop = False

    @classmethod
    def is_stopped(cls):
        return cls._stop








