import importlib
from hound import spiders
from hound.common.base_spider import BaseSpider
from hound.common import logger
from hound.memcache.url_cache import UrlCache

LOG = logger.get_logger(__name__)

class Crawler(object):

    def __init__(self):
        self.spiders = []
        self.url_cache = UrlCache()

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

    def run(self):
        print('start run crawl...')
        spiders_cls = self.get_all_spiders()
        for spider_cls in spiders_cls:
            spider_cls.start_spider()
            self.spiders.append(spiders_cls)
            spider_inst = spider_cls()
            spider_inst.start()

    def periodic_run(self):
        for (name, url_list) in self.url_cache:
            for spider_cls in self.spiders:
                if spider_cls.name == name:
                    spider_cls.start_spider()
                    spider_cls.urls = url_list
                    spider_inst = spider_cls()
                    spider_inst.start()







