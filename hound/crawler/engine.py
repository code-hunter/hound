from hound.spiders.wallstreet_spider import WallStreetSpider
import threading
from concurrent import futures
from hound.mq.local_queue import *

class Engine(object):

    def __init__(self):
        self.executor = futures.ThreadPoolExecutor(max_workers=32)
        self._stop = False
        self.queue = LocalQueue()

    def on_request(self, request):
        return request.getHtml()

    def stop(self):
        self._stop = True

    def start(self):
        threading.Thread(target=self.run).start()

    def run(self):
        while not self._stop:
            task = self.queue.get()
            print('get task : ' + task.id)

            spider_cls = task.spider_cls
            callback = task.callback
            url = task.url

            future = self.executor.submit(self.on_request, Request(url))
            html = future.result()

            spider_inst = spider_cls()
            spider_inst.on_callback(task.callback, html)


