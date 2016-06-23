#!/usr/bin/env python
# -*- coding: utf-8 -*-

import urlparse
import lxml.html
import json
from elasticsearch import Elasticsearch
from datetime import datetime, timedelta
from hound.model.archive import Archive
from hound.common.base_spider import BaseSpider

header = {
    "User-Agent": 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_4) AppleWebKit/537.36 (KHTML, like Gecko) '
                  'Chrome/50.0.2661.94 Safari/537.36',
    "Accept": "application/json",
    "X-Requested-With": "XMLHttpRequest"
}

es = Elasticsearch(hosts=["127.0.0.1"])
index_name = 'test'
doc_type = 'test'
es.indices.create(index=index_name, ignore=400)

urls = []


def get_geek_url(type, page_range=1, page_size=20):
    if type == "news":
        return "http://geek.csdn.net/service/news/get_category_news_list?category_id=news&username=&from=" + str(
            page_range) + "&size=" + str(page_size) + "&type=category"
    elif type == "author":
        data = es.search(index_name, doc_type, body={
            "aggs": {
                "authors": {
                    "terms": {
                        "field": "author",
                        "size": "15"
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
    return None

# get all author url list
get_geek_url("author")


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
    page_size = 20
    db_conn = 'elasticsearch://123.57.29.130:9300/elasticsearch/test/test'

    def start(self):
        return self.crawl(get_geek_url(self.type, page_range=0, page_size=self.page_size),
                         callback=self.result_to_json)

    def result_to_json(self, response):
        result = json.loads(response.content)
        status = result['status']
        has_more = result['has_more']
        if status != 1:
            print "no data at this request"
            return None

        data_list = []

        html_str = result["html"]
        if html_str is not None:
            data_list.extend(parse_html(html_str))

        # parse sub urls
        if has_more:
            # the range of response.url
            b_range = dict(urlparse.parse_qsl(urlparse.urlsplit(response.url).query))['from']

            # the current range that b_range add page_size
            page_range = self.page_size + int(b_range)
            self.crawl(get_geek_url(self.type, page_range=page_range), type='page', callback=self.result_to_json)

        return data_list


class GeekAuthorSpider(BaseSpider):
    name = "geek_author.csdn_spider"
    db_conn = 'elasticsearch://127.0.0.1:9300/truecloud_db_development/test/test'

    def __init__(self):
        super(GeekAuthorSpider, self).__init__()
        self.data_list = []
        self.page_range = 1
        self.current_author = ""

    def start(self):
        pass
        # if len(urls) > 0:
        #     return self.crawl(urls, callback=self.result_to_json, headers=header, cached=True)

    def result_to_json(self, response):
        result = json.loads(response.content)
        status = result['status']
        has_more = result['has_more']
        if status != 1:
            print "no data at this request"
            return None

        html_str = result["html"]
        if html_str == "":
            print "no html will be parsed"
            return None

        if html_str is not None:
            art_list = parse_html(html_str)
            if art_list is not None and len(art_list) > 0:
                self.data_list.extend(art_list)
        """
        if has_more:
            author = self.data_list[0].author
            if self.current_author == "" or self.current_author == author:
                self.page_range += 1
            else:
                self.page_range = 2
            self.current_author = author

            # sub request url
            r_url = self.get_author_data_url(author, self.page_range)
            self.crawl(r_url, type='page', callback=self.result_to_json)
        """
        return self.data_list

    def get_author_data_url(self, author, page_size=1):
        return "http://geek.csdn.net/user/publishlist/" + author + "/1/" + str(page_size)




if __name__ == "__main__":
    get_geek_url("author")
