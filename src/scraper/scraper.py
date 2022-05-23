import logging
from datetime import date
from datetime import datetime
import time
import random
from providers import Fetch
from scraper.parser import SearchParser
from storage import Storage
from math import ceil


class Scraper:

    def __init__(self, fetcher: Fetch, storage: Storage, search_parser: SearchParser):
        super().__init__()
        self.storage = storage
        self.search_parser = search_parser
        self.fetcher = fetcher
        self.search_url_templ = "https://www.etsy.com/de/search?q={}&page={}&ref=pagination"
        self.results_per_page = 64

    def scrape(self, keyword, fetch=True):

        num_pages = 1

        for page in range(0, num_pages+1):
            search_url = self.search_url_templ.format(keyword, page)
            content = self.fetcher.fetch(search_url)
            self.storage.save_file(search_url, content)
            result = self.search_parser.parse(content)
            num_pages = ceil(result["num_results"]/64)

        return {}
