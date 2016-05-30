from tornado.curl_httpclient import CurlAsyncHTTPClient
from tornado.httpclient import AsyncHTTPClient
from tornado.ioloop import IOLoop

class HttpClient(object):

    def __init__(self):
        self.io_loop = IOLoop()
        self.http_client = AsyncHTTPClient(CurlAsyncHTTPClient)