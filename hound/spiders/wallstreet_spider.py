import requests
import bs4
import re
import hashlib
from bs4 import BeautifulSoup
from elasticsearch import Elasticsearch
from hound.model.archive import Archive
from hound.common.base_spider import BaseSpider


class WallStreetSpider(BaseSpider):

    name = 'wallstreet_spider'
    urls = ['http://wallstreetcn.com/news?page=1','http://wallstreetcn.com/news?page=2']

    def start(self):
        return self.crawl('http://wallstreetcn.com/news?page=1', callback=self.parse1)

    def parse1(self, response):

        soup = BeautifulSoup(response, 'html.parser', from_encoding= 'utf8')

        # es = Elasticsearch(hosts=["localhost"])
        # indexName = 'hound'
        # doctypeName = 'crawler'
        # es.indices.create(index=indexName, ignore=400)

        # parser content : get title, href, summary

        sub_urls = []

        #save parse1 results
        for content in soup.find_all('div', class_ = 'content'):
            ret = content.find('div', class_ = 'summary hidden-xxs')
            if not ret:
                continue

            archiveInst = Archive()

            tag_title = content.a
            archiveInst.title =  tag_title.string.strip()
            archiveInst.orig_url =  tag_title.attrs['href']

            sub_urls.append(archiveInst.orig_url)

            archiveInst.md5 = hashlib.md5(archiveInst.orig_url).hexdigest()

            tag_author = content.find('span', class_ = 'meta author')
            archiveInst.author = tag_author.a.string

            tag_time = content.find('span', class_ = 'meta time visible-lg-inline-block')

            archiveInst.create_time = tag_time.string
            tag_summary = content.find('div', class_ = 'summary hidden-xxs')
            archiveInst.summary = tag_summary.string.strip()

            print archiveInst.as_dict()

            # es.create(index=indexName, doc_type=doctypeName, body = archiveInst.as_dict())

        #parse sub urls
        for sub_url in sub_urls:
            self.crawl(sub_url, callback=self.parse2)

    def parse2(self, response):
        print 'parse2'





