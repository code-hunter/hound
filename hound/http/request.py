import requests


class Request(object):

    def __init__(self, url):

        self.url = url

    def getHtml(self):

        ret = requests.get(self.url)
        return ret.content.decode('utf8')

