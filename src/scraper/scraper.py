import logging
from datetime import date
from datetime import datetime
import time
import random
from scraper.providers import Fetch
from scraper.parser import SearchParser
from scraper.storage import Storage
from math import ceil
from concurrent.futures import ThreadPoolExecutor, as_completed


class Scraper:

    def __init__(self, fetcher: Fetch, storage: Storage, search_parser: SearchParser, num_workers=10):
        super().__init__()
        self.storage = storage
        self.search_parser = search_parser
        self.fetcher = fetcher
        self.search_url_templ = "https://www.etsy.com/de/search?q={}&page={}&ref=pagination"
        self.results_per_page = 64
        self.num_workers = num_workers

    def _fetch(self, url):
        content = self.fetcher.fetch(url)
        self.storage.save_file(url, content)

        return content

    def scrape(self, keyword, num_pages=None, fetch=True):
        futures = []
        pages = []

        with ThreadPoolExecutor(max_workers=self.num_workers) as executor:
            if num_pages is None:
                num_pages = 1

            for page in range(0, num_pages):
                search_url = self.search_url_templ.format(keyword, page)
                pages.append(search_url)
                futures.append(executor.submit(self._fetch, url=search_url))

                if page == 0 and as_completed(futures):
                    content = self._fetch(search_url)
                    result = self.search_parser.parse(content)
                    if num_pages is None:
                        num_pages = ceil(result["num_results"]/64)

        return pages
