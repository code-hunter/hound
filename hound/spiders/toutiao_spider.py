#!/usr/bin/env python
# -*- coding: utf-8 -*-

import urllib
import hashlib
import lxml.html
from requests import request
from datetime import datetime, timedelta
from hound.model.archive import Archive
from hound.common.base_spider import BaseSpider


header = {
    "User-Agent": 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_4) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/50.0.2661.94 Safari/537.36'
}

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


def get_redirect_url(url):
    r = request("get", url, allow_redirects=False, headers=header)
    return r.headers["location"].split("?")[0]


class ToutiaoSpider(BaseSpider):
    name = "tooutiao.io_spider"
    db_conn = 'elasticsearch://192.168.10.67:9300/truecloud_db_development/test/test'

    def start(self):
        return self.crawl(urls, callback=self.parse)

    def parse(self, response):
        result = []
        page = lxml.html.fromstring(response.decode('utf-8'))
        for ele in page.find_class("post"):
            art = Archive()
            art.website = "toutiao.io"
            art.author = ele.find_class('subject-name')[0].cssselect("a")[0].text_content()

            # get redirect url by toutiao url
            art.title = ele.find_class('title')[0].cssselect("a")[0].text_content()
            tmp_url = ele.find_class('title')[0].cssselect("a")[0].attrib['href']
            art.url = get_redirect_url(tmp_url)

            # url encode
            # url_q = urllib.quote(art.url.encode("utf8"))
            # art.md5 = hashlib.md5(url_q).hexdigest()
            art.create_time = datetime.now()
            result.append(art)
        return result

