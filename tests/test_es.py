import datetime
from elasticsearch import Elasticsearch
from hound.model.archive import Archive

es = Elasticsearch(hosts=["192.168.10.67"])
index_name = 'test'
doc_type = 'test'
es.indices.create(index=index_name, ignore=400)


art = Archive()
art.website = "geek.csdn.net11111111"
art.url = 'http://tech.163.com/16/0602/11/BOI68UKE00097U7V.html'
art.author_url = 'http://geek.csdn.net/user/publishlist/karamos'
art.author = 'karamos11111111111'
art.md5 = 'dba32bbe2c28ec2d8260d369cd2d84b0'
art.create_time = datetime.datetime.now()

