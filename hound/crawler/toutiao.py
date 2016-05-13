from requests import request, sessions
from lxml import etree
import lxml.html
import datetime
from hound.model.archive import Archive
from elasticsearch import Elasticsearch
import random
import hashlib

header = {
    "User-Agent": 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_4) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/50.0.2661.94 Safari/537.36'
}

es = Elasticsearch(hosts=["192.168.10.67"])
index_name = 'hound'
doc_type = 'crawler'
es.indices.create(index=index_name, ignore=400)


class ToutiaoParser(object):
    def __init__(self, r_url, proxies=None):
        self.proxies = proxies
        if not r_url:
            return
        article_list = self._find_url(r_url)
        data_list = []
        for article in article_list:
            s_url = self._find_redirect_url(article.url)
            article.url = s_url
            data_list.append(article)
        print 'r_url : %s ,list size : %d' % (r_url, len(data_list))
        # save article list
        self._save(data_list)

    def _find_url(self, url):
        proxies = {}
        if self.proxies is not None:
            proxies = random.choice(self.proxies)
        article_list = []
        resp = request("get", url, headers=header, proxies = proxies)
        if resp.status_code == 404:
            return article_list
        page = lxml.html.fromstring(resp.text)
        for ele in page.find_class("post"):
            '''
            article = {
                'up': ele.find_class("like-button")[0].cssselect('span')[0].text_content(),
                't_url': ele.find_class('title')[0].cssselect("a")[0].attrib['href'],
                'title': ele.find_class('title')[0].cssselect("a")[0].text_content(),
                'author_name': ele.find_class('subject-name')[0].cssselect("a")[0].text_content(),
                'author_url': "http://toutiao.io" +ele.find_class('subject-name')[0].cssselect("a")[0].attrib['href']
            }
            '''
            art = Archive()
            art.website = url
            art.author = ele.find_class('subject-name')[0].cssselect("a")[0].text_content()
            art.title = ele.find_class('title')[0].cssselect("a")[0].text_content()
            art.url = ele.find_class('title')[0].cssselect("a")[0].attrib['href']
            art.md5 = hashlib.md5(art.url).hexdigest()
            art.create_time = datetime.datetime.now()

            article_list.append(art)
        return article_list

    def _find_redirect_url(self, url):
        proxies = {}
        if self.proxies is not None:
            proxies = random.choice(self.proxies)
        r = request("get", url, headers=header, allow_redirects=False, proxies=proxies)
        return r.headers["location"].split("?")[0]

    def _save(self, arts):
        if arts is None or len(arts) == 0:
            return
        for art in arts:
            es.create(index=index_name, doc_type=doc_type, body=art.as_dict())


if __name__ == "__main__":

    print datetime.datetime.now()

    data = es.search("ip", 'proxy_info', body={
        "query": {
            "bool": {
                "must": [
                    {"match": {
                        "protocol": "http"
                    }}
                ]
            }
        }
    }, suggest_size=10)

    proxy_lit = []
    for d in data['hits']['hits']:
        ip = d['_source']['ip']
        port = d['_source']['port']
        protocol = d['_source']['protocol']
        proxy = {
            protocol: "http://"+ip+":"+port
        }
        proxy_lit.append(proxy)

    url = "http://toutiao.io/prev/"
    format_str = '%Y-%m-%d'

    #date sub
    date_str = '2014-09-27'
    old_date = datetime.datetime.strptime(date_str, format_str)
    now_date = datetime.datetime.now()

    days = (now_date-old_date).days
    for day in range(days):
        old_date += datetime.timedelta(days=1)
        ToutiaoParser(url+datetime.datetime.strftime(old_date, format_str))

    print datetime.datetime.now()
