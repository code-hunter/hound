# -*- coding: utf-8 -*-

import requests
import bs4
from hound.model.proxyinfo import ProxyInfo
from elasticsearch import Elasticsearch

DATA_LIST = []


def get_ip84_url(num=2):
    url_list = []
    url = 'http://www.ip84.com/gn/'
    for i in range(1, num):
        url_list.append(url + str(i))
    return url_list


def ip84_get():
    data_list = []
    url_list = get_ip84_url()
    for url in url_list:
        data_list.append(get_data_of_ip84(url))
    return data_list


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


class IpGet(object):
    def __init__(self):
        global DATA_LIST
        if len(DATA_LIST) > 0:
            return
        # proxy list
        proxies = []
        data_list = ip84_get()
        for data in data_list[0]:
            proxy = {
                data.protocol: data.protocol+"://"+data.ip+":"+data.port
            }
            proxies.append(proxy)
        DATA_LIST = proxies

    def get_proxy_list(self):
        return DATA_LIST


if __name__ == "__main__":
    list = IpGet().get_proxy_list()
    print "%d " % len(list)

    list1 = IpGet().get_proxy_list()
    list2 = IpGet().get_proxy_list()
    list3 = IpGet().get_proxy_list()

