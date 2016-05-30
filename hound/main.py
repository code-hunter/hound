from hound.crawler.crawler import Crawler
from tornado import gen
from tornado.ioloop import IOLoop


if __name__ == '__main__':
    @gen.coroutine
    def run():
        crawler = Crawler()
        yield crawler.run()

    ioloop = IOLoop().current()
    ioloop.run_sync(run)

