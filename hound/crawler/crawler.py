import time
import importlib
import threading
from hound import spiders
import tornado
from tornado.ioloop import IOLoop
from tornado import gen
from hound.mq import get_mq
from hound.common.base_spider import BaseSpider
from hound.http.httpclient import HttpClient
from hound.common import logger
from hound.memcache.result_cache import ResultCache
from hound.model.archive import Archive
from hound.model.task import Task
from hound.model.task_chain import TaskChain

LOG = logger.get_logger(__name__)

class Crawler(object):

    def __init__(self):
        self.task_queue = get_mq()
        self.http_client = HttpClient()
        self.result_cache = ResultCache()
        self.fetcher = None
        self._stop = False

    def load_module(self, module_name):
        try:
            module = importlib.import_module(module_name)

            if not module:
                _msg = 'failed to load module'
                LOG.error(_msg)
                return None
            return module
        except ImportError as e:
            raise e

    def get_all_spiders(self):
        spiderscls = []
        for spider in spiders.all_spiders:
            spider_filename = spider.split('.')[-1]
            module = self.load_module(spider)

            for attr_name in dir(module):
                attr = getattr(module, attr_name)

                if isinstance(attr, type) and \
                        issubclass(attr, BaseSpider) and \
                        attr.__dict__['__module__'].endswith(spider_filename):
                    spiderscls.append(attr)
        return spiderscls

    def start(self):
        threading.Thread(target=self.run).start()

    @gen.coroutine
    def do_task(self, task):
        task.start_time = time.time()
        spider_cls = task.spider_cls

        spider_inst = task.spider_cls()
        if spider_cls.is_stopped():
            LOG.info('spider : %s has been stopped.' % (spider_inst.name) )
            return
        response = yield self.http_client.fetch(task.url, **task.request_params)
        result = spider_inst.on_callback(task.callback, response.body)
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

        print('start running...')
        @gen.coroutine
        def task_loop():
            while not self._stop:
                try:
                    item = yield self.task_queue.get()
                    if isinstance(item, Task):
                        yield self.do_task(item)
                    elif isinstance(item, TaskChain):
                        yield self.do_task_chain(item)

                finally:
                    self.task_queue.task_done()
                    # break

        # @gen.coroutine
        # def worker():
        #     while True:
        #         yield task_loop()

        spiders_cls = self.get_all_spiders()
        for spider_cls in spiders_cls:
            spider_cls.start_spider()
            spider_inst = spider_cls()
            spider_inst.start()

        yield task_loop()

        # for i in range(5):
        #     worker()
        #
        # yield self.task_queue.join()

if __name__ == '__main__':
    @gen.coroutine
    def main():
        crawler = Crawler()
        yield crawler.run()

    ioloop = IOLoop().current()
    ioloop.run_sync(main)




