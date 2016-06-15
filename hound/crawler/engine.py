import time
import importlib
import threading
from concurrent import futures
from tornado import gen
from hound.mq import get_mq
from hound.common.base_spider import BaseSpider
from hound.http.httpclient import HttpClient
from hound.http.response import Response
from hound.common import logger
from hound.memcache.result_cache import ResultCache
from hound.model.archive import Archive
from hound.model.task import Task
from hound.model.task_chain import TaskChain

LOG = logger.get_logger(__name__)

class Engine(object):

    def __init__(self, coroutine_size=8):
        self.task_queue = get_mq()
        self.http_client = HttpClient()
        self.result_cache = ResultCache()
        self.coroutine_size = coroutine_size
        self.fetcher = None
        self._stop = False

    @gen.coroutine
    def do_task(self, task):
        task.start_time = time.time()
        spider_cls = task.spider_cls

        spider_inst = task.spider_cls()
        if spider_cls.is_stopped():
            LOG.info('spider : %s has been stopped.' % (spider_inst.name) )
            return
        result = yield self.http_client.fetch(task.url, **task.request_params)

        response = Response()
        response.url = task.url
        response.content = result.body

        result = spider_inst.on_callback(task.callback, response)
        task.end_time = time.time()
        print(str('task url : ' + task.url))

        if result:
            result, stop_spider = spider_inst.check_result(task, result)

            if result:

                if isinstance(result, list):
                    print('fetch %s new papers.' % (str(len(result))))
                    for item in result:
                        print(item.as_dict())
                elif isinstance(result, Archive):
                    print('fetch 1 new papers')
                    print(result.as_dict())

                if task.cached :
                    spider_inst.on_cache(task, result)

                if isinstance(result, list) or isinstance(result, dict) or isinstance(result, Archive):
                    spider_inst.on_save(task, result)
            else:
                print('no new paper found.')

            if stop_spider:
                spider_cls.stop_spider()

    @gen.coroutine
    def do_task_chain(self, task_chain):

        while task_chain.size() > 0:
            task = task_chain.get()
            if not task.spider_cls.is_stopped():
                yield self.do_task(task)
            else:
                print('spider has been stopped')
                break


    @gen.coroutine
    def run(self):

        print('start run engine...')
        @gen.coroutine
        def task_loop():
            # while not self._stop:
            try:
                item = yield self.task_queue.get()
                if isinstance(item, Task):
                    yield self.do_task(item)
                elif isinstance(item, TaskChain):
                    yield self.do_task_chain(item)

            finally:
                self.task_queue.task_done()
                    # break

        @gen.coroutine
        def worker():
            while True:
                yield task_loop()

        # yield task_loop()

        for _ in range(self.coroutine_size):
            worker()

        yield self.task_queue.join()

