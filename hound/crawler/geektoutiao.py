#!/usr/bin/env python
#
# Licensed under the Apache License, Version 2.0 (the "License"); you may
# not use this file except in compliance with the License. You may obtain
# a copy of the License at
#
# http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
# WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
# License for the specific language governing permissions and limitations
# under the License.

# -*- coding: utf-8 -*-

# author : sticver
# email : sticver@google.com

import urllib
import hashlib
import lxml.html
import datetime
import random
from requests import request
from hound.model.archive import Archive
from elasticsearch import Elasticsearch
from hound.common.ipget import IpGet

header = {
    "User-Agent": 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_4) AppleWebKit/537.36 (KHTML, like Gecko) '
                  'Chrome/50.0.2661.94 Safari/537.36',
    "Accept": "application/json",
    "X-Requested-With": "XMLHttpRequest"
}

es = Elasticsearch(hosts=["192.168.10.67"])
index_name = 'hound'
doc_type = 'crawler'
es.indices.create(index=index_name, ignore=400)

# proxy ip list
proxies = IpGet().get_proxy_list()


def find_proxy():
    proxy = {}
    if proxies is not None:
        proxy = random.choice(proxies)
    return proxy


class GeekToutiaoParser(object):
    def __init__(self, proxies=None, type=None):
        self.size = 40
        self.count = 0
        self.proxies = proxies
        if type == "news":
            self._news_parse_json()
        elif type == "author":
            self._author_parse()
        else:
            self._hack_count_parse_json()

    def _news_parse_json(self, page_range=0):
        r_url = "http://geek.csdn.net/service/news/get_category_news_list?category_id=news&username=&from=" + str(
            page_range) + "&size=" + str(self.size) + "&type=category"
        resp = request("get", r_url, headers=header, proxies=find_proxy())
        if resp.status_code == 200:
            result = resp.json()
            status = result['status']
            has_more = result['has_more']
            if status != 1:
                print "no data at this request"
                return
            html_str = result["html"]
            data_list = self._parse_html(html_str, r_url)
            if len(data_list) > 0:
                self._save(data_list)
            if has_more:
                self._news_parse_json(page_range=(page_range + self.size))

    def _hack_count_parse_json(self, page_range="-", type="HackCount"):
        r_url = 'http://geek.csdn.net/service/news/get_news_list?from=' + page_range + '&size=20&type=' + type
        resp = request("get", r_url, headers=header, proxies=find_proxy())
        if resp.status_code == 200:
            content = resp.json()
            status = content['status']
            if status != 1:
                return
            p_range = content['from']
            has_more = content['has_more']
            html_str = content['html']
            print 'page_range : %s ' % page_range

            data_list = self._parse_html(html_str, r_url)
            if len(data_list) > 0:
                self._save(data_list)
            if has_more:
                self._hack_count_parse_json(p_range, type)

    def _parse_html(self, data, website):
        data_list = []
        page = lxml.html.fromstring(data)
        for ele in page.find_class("geek_list"):
            art = Archive()
            art.website = website
            art.url = ele.find_class("title")[0].attrib['href'].split("?")[0]
            art.title = ele.find_class("title")[0].text_content()
            art.author_url = ele.find_class("right")[0].cssselect("a")[0].attrib['href']
            art.author = art.author_url.split("/")[-1]
            url_q = urllib.quote(art.url.encode("utf8"))
            art.md5 = hashlib.md5(url_q).hexdigest()
            art.create_time = datetime.datetime.now()
            data_list.append(art)
        return data_list

    def _save(self, data_list):
        print "archive list size : %d" % len(data_list)
        for art in data_list:
            es.create(index=index_name, doc_type=doc_type, body=art.as_dict())

    def _author_parse(self):
        data = es.search(index_name, doc_type, body={
            "aggs": {
                "authors": {
                    "terms": {
                        "field": "author",
                        "size": "0"
                    }
                }
            }
        }, suggest_size=10)
        author_list = data['aggregations']['authors']['buckets']
        print "author list size : %d " % len(author_list)

        for author in author_list:
            self._author_parse_json(author['key'])

    def _author_parse_json(self, author, page_size=0):
        r_url = "http://geek.csdn.net/user/publishlist/" + author + "/" + str(page_size)
        resp = request("get", r_url, headers=header, proxies=find_proxy())
        if resp.status_code is not 200:
            print "request failure : %d" % resp.status_code
            return

        content = resp.json()
        if content["status"] is False:
            return
        # parse html and get archive data list
        html_str = content['html']
        if html_str == "":
            print "no html will be parsed,author : %s, page_size : %d" % (author, page_size)
            return

        data_list = self._parse_html(html_str, r_url)
        if len(data_list) > 0:
            self._save(data_list)
        if content["has_more"]:
            page_size += 1
            self._author_parse_json(author, page_size)


if __name__ == '__main__':
    #gt_news = GeekToutiaoParser(type="news")

    gt_author = GeekToutiaoParser(type="author")
