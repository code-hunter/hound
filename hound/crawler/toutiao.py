from requests import request, sessions
from lxml import etree
import lxml.html
import datetime
from hound.model.archive import Archive
from elasticsearch import Elasticsearch

header = {
    "User-Agent": 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_4) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/50.0.2661.94 Safari/537.36'
}

es = Elasticsearch(hosts=["192.168.10.67"])
indexName = 'hound'
doctypeName = 'crawler'
es.indices.create(index=indexName, ignore=400)


class ToutiaoParser(object):
    def __init__(self, url):
        if not url:
            return
        article_list = self._find_url(url)
        data_list = []
        for article in article_list:
            s_url = self._find_redirect_url(article.url)
            article.url = s_url
            print 'redirect_url : %s ' % s_url
            data_list.append(article)
        print 'list size : %d' % len(data_list)
        # save article list
        self._save(data_list)

    def _find_url(self, url):
        article_list = []
        resp = request("get", url, headers=header)
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

            article_list.append(art)
        return article_list

    def _find_redirect_url(self, url):
        r = request("get", url, headers=header, allow_redirects=False)
        return r.headers["location"].split("?")[0]

    def _save(self, arts):
        if arts is None or len(arts) == 0:
            return
        for art in arts:
            es.create(index=indexName, doc_type=doctypeName, body=art.as_dict())


if __name__ == "__main__":
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
