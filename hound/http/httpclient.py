# from tornado.curl_httpclient import CurlAsyncHTTPClient
from tornado.httpclient import AsyncHTTPClient
from tornado.httpclient import HTTPRequest
from tornado.ioloop import IOLoop
from tornado import gen
import tornado

class HttpClient(object):

    def __init__(self, maxsize=64, **kwargs):
        self.http_client = AsyncHTTPClient()
        # self.http_client.configure(CurlAsyncHTTPClient)

    @gen.coroutine
    def on_request(self, url, **kwargs):
        http_request = HTTPRequest(url=url, **kwargs)
        try:
            response = yield gen.maybe_future(self.http_client.fetch(http_request))
        except tornado.httpclient.HTTPError as e:
            raise e

        raise gen.Return(response)

    @gen.coroutine
    def fetch(self, url, **kwargs):
        response = yield self.on_request(url, **kwargs)
        raise gen.Return(response)


# if __name__ == '__main__':
#     io_loop = IOLoop.instance()
#     client = HttpClient()
#
#     headers = {
#     "User-Agent": 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_4) AppleWebKit/537.36 (KHTML, like Gecko) '
#                   'Chrome/50.0.2661.94 Safari/537.36',
#     "Accept": "application/json",
#     "X-Requested-With": "XMLHttpRequest"
#     }
#
#
#     io_loop.run_sync(lambda : client.fetch('http://geek.csdn.net/user/publishlist/wanghui_777/1', headers=headers))
#
#




