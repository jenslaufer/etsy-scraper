import re
import requests
from pyuseragent.useragent import UserAgent


class Fetch:
    def __init__(self, proxies=None):
        self.proxies = proxies
        self.regex = r'(http://)([a-z0-9A-Z]+):([a-z0-9A-Z]+)@([0-9\.]+):([0-9]+)'

    def get_proxy(self):
        proxy = self.proxies.get()['http']
        res = re.search(self.regex, proxy)

        username = res.group(2)
        password = res.group(3)
        host = res.group(4)
        port = res.group(5)

        return (username, password, host, port)


class RequestsFetch(Fetch):

    def __init__(self, proxies=None):
        super(RequestsFetch, self).__init__(proxies)
        self.useragents = UserAgent()

    def fetch(self, url):
        s = requests.session()
        headers = {
            'User-Agent': "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:95.0) Gecko/20100101 Firefox/95.0",
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8',
        }
        if self.proxies is not None:
            proxies = self.proxies.get()
            return s.get(url, headers=headers, proxies=proxies).content
        else:
            return s.get(url, headers=headers).content
