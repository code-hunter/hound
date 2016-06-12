# -*- coding: utf-8 -*-

import requests
import bs4
from hound.memcache.proxy_cache import ProxyCache
from hound.model.proxyinfo import ProxyInfo


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
        proxy_cache = ProxyCache()
        data_list = ip84_get()
        for data in data_list[0]:
            proxy_cache.put((data.ip, data.port, data.protocol))


if __name__ == "__main__":
    IpGet()
    cache = ProxyCache()
    print cache.get()