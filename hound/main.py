import requests
import bs4
import re
import hashlib
from bs4 import BeautifulSoup
from elasticsearch import Elasticsearch
from hound.model.archive import Archive

url = 'http://wallstreetcn.com/news?page=1'

ret = requests.get(url)
soup = BeautifulSoup(ret.content.decode('utf8'), 'html.parser', from_encoding= 'utf8')

es = Elasticsearch(hosts=["localhost"])
indexName = 'hound'
doctypeName = 'crawler'
es.indices.create(index=indexName, ignore=400)

# parser content : get title, href, summary,

for content in soup.find_all('div', class_ = 'content'):
    ret = content.find('div', class_ = 'summary hidden-xxs')
    if not ret:
        continue

    archiveInst = Archive()

    tag_title = content.a
    archiveInst.title =  tag_title.string.strip()
    archiveInst.orig_url =  tag_title.attrs['href']
    archiveInst.md5 = hashlib.md5(archiveInst.orig_url).hexdigest()

    tag_author = content.find('span', class_ = 'meta author')
    archiveInst.author = tag_author.a.string

    tag_time = content.find('span', class_ = 'meta time visible-lg-inline-block')

    archiveInst.create_time = tag_time.string
    tag_summary = content.find('div', class_ = 'summary hidden-xxs')
    archiveInst.summary = tag_summary.string.strip()

    es.create(index=indexName, doc_type=doctypeName, body = archiveInst.as_dict())




