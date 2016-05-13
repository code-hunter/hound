# -*- coding: utf-8 -*-

import requests
import bs4
from hound.model.proxyinfo import ProxyInfo
from elasticsearch import Elasticsearch

es = Elasticsearch(hosts=["192.168.10.67"])
index_name = 'ip'
doc_type = 'proxy_info'
es.indices.create(index=index_name, ignore=400)


def get_data_of_ip84(url):
    ip_list = []
    rsp = requests.get(url)
    print "request status : %s ", rsp.status_code
    soup = bs4.BeautifulSoup(rsp.text, "lxml")
    for tr in soup.find_all("tr"):
        pi = ProxyInfo()
        tds = tr.find_all("td")
        if len(tds) == 0:
            continue
        pi.ip = tds[0].text
        pi.port = tds[1].text
        pi.area = tds[2].text
        pi.level = tds[3].text
        pi.protocol = tds[4].text
        pi.speed = tds[5].text
        pi.isValid = tds[6].text
        ip_list.append(pi)
    return ip_list

def get_ip84_url(num):
    url_list = []
    url = 'http://www.ip84.com/gn/'
    for i in range(1, num):
        url_list.append(url+str(i))
    return url_list


def ip84():
    num = 10
    data_list = []
    url_list = get_ip84_url(num)
    for url in url_list:
        data_list.append(get_data_of_ip84(url))

    for ip_lis in data_list:
        for pi in ip_lis:
            es.create(index_name,doc_type,pi.as_dict())

if __name__ == "__main__":
    ip84()