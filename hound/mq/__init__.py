
from .local_queue import LocalQueue
from .tornado_queue import TornadoQueue

def get_mq():

    return TornadoQueue()
