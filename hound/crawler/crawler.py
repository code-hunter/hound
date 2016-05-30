import importlib
import threading
from hound import spiders
import tornado
from tornado.ioloop import IOLoop
from tornado import gen
from hound.mq.local_queue import LocalQueue
from hound.common.base_spider import BaseSpider
from hound.http.httpclient import HttpClient
from hound.common import logger
from hound.memcache.result_cache import ResultCache

LOG = logger.get_logger(__name__)

class Crawler(object):

    def __init__(self):
        self.task_queue = LocalQueue()
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
    def run(self):

        print('start running...')
        @gen.coroutine
        def task_loop():
            while not self._stop:

                task = self.task_queue.get()

                response = yield self.http_client.fetch(task.url)
                spider_inst = task.spider_cls()
                spider_inst.on_callback(task.callback, response.body)

        spiders_cls = self.get_all_spiders()
        for spider_cls in spiders_cls:
            spider_inst = spider_cls()
            spider_inst.start()

        yield task_loop()

if __name__ == '__main__':
    @gen.coroutine
    def main():
        crawler = Crawler()
        yield crawler.run()

    ioloop = IOLoop().current()
    ioloop.run_sync(main)




