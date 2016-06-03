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
    db_conn = 'elasticsearch://localhost:9300/local-es/hound/crawler'
    urls = ['http://wallstreetcn.com/news?page=1','http://wallstreetcn.com/news?page=2']

    def start(self):
        return self.crawl('http://wallstreetcn.com/news?page=1',page_range=[],  callback=self.parse1)

    def parse1(self, response):

        soup = BeautifulSoup(response, 'html.parser', from_encoding= 'utf8')

        sub_urls = []
        result = []
        #save parse1 results
        for content in soup.find_all('div', class_ = 'content'):
            ret = content.find('div', class_ = 'summary hidden-xxs')
            if not ret:
                continue

            archiveInst = Archive()

            tag_title = content.a
            archiveInst.title =  tag_title.string.strip()
            archiveInst.url =  tag_title.attrs['href']

            sub_urls.append(archiveInst.url)

            archiveInst.md5 = hashlib.md5(archiveInst.url).hexdigest()

            tag_author = content.find('span', class_ = 'meta author')
            archiveInst.author = tag_author.a.string

            tag_time = content.find('span', class_ = 'meta time visible-lg-inline-block')

            archiveInst.published_time = tag_time.string
            tag_summary = content.find('div', class_ = 'summary hidden-xxs')
            archiveInst.summary = tag_summary.string.strip()

            print archiveInst.as_dict()

            result.append(archiveInst)

        #parse sub urls
        for sub_url in sub_urls:
            self.crawl(sub_url, callback=self.parse2)

        return result

    def parse2(self, response):
        print 'parse2'



