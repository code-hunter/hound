#!/usr/bin/env python
# -*- coding: utf-8 -*-

import urllib
import hashlib
import lxml.html
from datetime import datetime, timedelta
from bs4 import BeautifulSoup
from hound.model.archive import Archive
from hound.common.base_spider import BaseSpider

"""
header = {
    "User-Agent": 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_4) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/50.0.2661.94 Safari/537.36'
}
"""

urls=[]
format_str = '%Y-%m-%d'
toutiao_url = "http://toutiao.io/prev/"


def count_urls():
    """
    statistic from 2014-09-27 to now,the number fo days and put it to url list.
    """
    old_date = datetime.strptime("2014-09-27", format_str)
    days = (datetime.now() - old_date).days
    for day in range(days):
        old_date += timedelta(days=1)
        urls.append(toutiao_url + datetime.strftime(old_date, format_str))

count_urls()


class ToutiaoSpider(BaseSpider):
    name = "tooutiao.io_spider"

    def start(self):
        return self.crawl(urls[-1], callback=self.parse)

    def parse(self, response):
        # page = BeautifulSoup(response, 'lxml', from_encoding='utf8')
        page = lxml.html.fromstring(response)
        for ele in page.find_class("post"):
            art = Archive()
            art.website = "toutiao.io"
            art.author = ele.find_class('subject-name')[0].cssselect("a")[0].text_content()
            art.title = ele.find_class('title')[0].cssselect("a")[0].text_content()
            art.url = ele.find_class('title')[0].cssselect("a")[0].attrib['href']
            # url encode
            url_q = urllib.quote(art.url.encode("utf8"))
            art.md5 = hashlib.md5(url_q).hexdigest()
            art.create_time = datetime.now()
            print art.as_dict()

