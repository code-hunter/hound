from hound.crawler.crawler import Crawler
from hound.crawler.engine import Engine
import tornado
from tornado import gen
from tornado.ioloop import IOLoop


if __name__ == '__main__':

    def start_crawler():
        crawler = Crawler()
        crawler.run()

    @gen.coroutine
    def start_engine():
        engine = Engine()
        yield engine.run()

    ioloop = IOLoop().current()
    # ioloop.run_sync(run)
    tornado.ioloop.PeriodicCallback(start_crawler, 10000,
                                        io_loop=ioloop).start()
    start_engine()
    ioloop.start()
