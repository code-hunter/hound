
class Task(object):
    '''task model '''

    def __init__(self):
        self.id = None
        self.url = None
        self.spider_cls = None
        self.func = None
        self.kwargs = None
        self.callback = None
        self.message = None
        self.status = None
        self.result = None
        self.start_time = None
        self.end_time = None

