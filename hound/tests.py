import random
import time
from tornado import gen
from tornado.ioloop import IOLoop


# @gen.coroutine
# def get_url(url):
#     wait_time = random.randint(1, 4)
#     yield gen.sleep(wait_time)
#     print('URL {} took {}s to get!'.format(url, wait_time))
#     raise gen.Return((url, wait_time))
#
#
# @gen.coroutine
# def outer_coroutine():
#     before = time.time()
#     coroutines = [get_url(url) for url in ['URL1', 'URL2', 'URL3']]
#     result = yield coroutines
#     after = time.time()
#     print(result)
#     print('total time: {} seconds'.format(after - before))
#
# if __name__ == '__main__':
#     IOLoop.current().run_sync(outer_coroutine)


#
# @gen.coroutine
# def test(i):
#     print(str(i))
#     yield gen.sleep(1)
#
# @gen.coroutine
# def work(i):
#     while True:
#         yield test(i)
#
# @gen.coroutine
# def main():
#     for x in range(5):
#         test = work(x)
#         print('')
#
# ioloop = IOLoop().instance()
#
# ioloop.run_sync(lambda : test(1))
# ioloop.start()

# @gen.coroutine
# def minute_loop():
#     while True:
#         print('hello')
#         yield gen.sleep(1)
#
# # Coroutines that loop forever are generally started with
# # spawn_callback().
# IOLoop.current().spawn_callback(minute_loop)
# IOLoop.current().start()
#

from datetime import datetime
dt = datetime(1970, 1, 2, 0, 0)
print(dt.timestamp())