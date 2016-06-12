from hound.crawler.crawler import Crawler
import tornado
from tornado import gen
from tornado.ioloop import IOLoop


if __name__ == '__main__':
    @gen.coroutine
    def run():
        crawler = Crawler()
        yield crawler.run()

    ioloop = IOLoop().current()
    # ioloop.run_sync(run)
    tornado.ioloop.PeriodicCallback(run, 10000,
                                        io_loop=ioloop).start()
    ioloop.start()
