#!/usr/bin/env python
# -*- coding: utf-8 -*-

import urllib
import hashlib
import lxml.html
import json
from elasticsearch import Elasticsearch
from datetime import datetime, timedelta
from hound.model.archive import Archive
from hound.common.base_spider import BaseSpider

es = Elasticsearch(hosts=["192.168.10.67"])
index_name = 'hound'
doc_type = 'crawler'
es.indices.create(index=index_name, ignore=400)

urls = []


def get_geek_url(type, page_range=0, page_size=20):
    if type == "news":
        return "http://geek.csdn.net/service/news/get_category_news_list?category_id=news&username=&from=" + str(
            page_range) + "&size=" + str(page_size) + "&type=category"
    elif type == "author":
        data = es.search(index_name, doc_type, body={
            "aggs": {
                "authors": {
                    "terms": {
                        "field": "author",
                        "size": "0"
                    }
                }
            },
            "query": {
                "bool": {
                    "must": [
                        {
                            "wildcard": {"website": "geek*"}
                        }
                    ]
                }
            }
        }, suggest_size=10)
        author_list = data['aggregations']['authors']['buckets']
        print "author list size : %d " % len(author_list)

        r_url = "http://geek.csdn.net/user/publishlist/%s/" + str(page_range)
        for author in author_list:
            author_url = r_url % author['key']
            urls.append(author_url)


def parse_html(data):
    """
    parse data and get url ,title ,author
    :param data: html str
    :return: archive list
    """
    data_list = []
    page = lxml.html.fromstring(data)
    for ele in page.find_class("geek_list"):
        art = Archive()
        art.website = "geek.csdn.net"
        art.url = ele.find_class("title")[0].attrib['href'].split("?")[0]
        art.title = ele.find_class("title")[0].text_content()
        art.author_url = ele.find_class("right")[0].cssselect("a")[0].attrib['href']
        art.author = art.author_url.split("/")[-1]
        # url_q = urllib.quote(art.url.encode("utf8"))
        # art.md5 = hashlib.md5(url_q).hexdigest()
        art.create_time = datetime.now()

        data_list.append(art)
    return data_list


class GeekNewsSpider(BaseSpider):
    name = "geek.csdn_spider"
    type = "news"
    db_conn = 'elasticsearch://192.168.10.67:9300/truecloud_db_development/test/test'

    def __init__(self):
        super(GeekNewsSpider, self).__init__()
        self.page_range = 0
        self.page_size = 20

    def start(self):
        return self.crawl(get_geek_url(self.type, page_range=self.page_range, page_size=self.page_size),
                          callback=self.result_to_json)

    def result_to_json(self, response):
        result = json.loads(response)
        status = result['status']
        has_more = result['has_more']
        if status != 1:
            print "no data at this request"
            return None
        html_str = result["html"]
        if html_str is not None:
            return parse_html(html_str)

        # parse sub urls
        if has_more:
            self.page_range += self.page_size
            self.crawl(get_geek_url(self.type, ), type='page', callback=self.result_to_json)

        return None


class GeekAuthorSpider(BaseSpider):
    name = "geek_author.csdn_spider"

    def start(self):
        get_geek_url("author")
        if len(urls) > 0:
            return self.crawl(urls[0], callback=self.result_to_json)

    def result_to_json(self, response):
        result = json.loads(response)
        status = result['status']
        has_more = result['has_more']
        if status != 1:
            print "no data at this request"
            return

        html_str = result["html"]
        if html_str == "":
            print "no html will be parsed"
            return

        if html_str is not None:
            return parse_html(html_str)
        return None


if __name__ == "__main__":
    get_geek_url("author")
