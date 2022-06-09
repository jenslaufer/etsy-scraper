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

    def __init__(self, fetcher: Fetch, storage: Storage,
                 search_parser: SearchParser,
                 collection_name="products",
                 num_fetch_workers=10, num_parsing_workers=50):
        super().__init__()

        self.storage = storage
        self.search_parser = search_parser
        self.fetcher = fetcher
        self.search_url_templ = "https://www.etsy.com/de/search?q={}&page={}&ref=pagination"
        self.results_per_page = 64
        self.num_fetch_workers = num_fetch_workers
        self.num_parsing_workers = num_parsing_workers
        self.collection_name = collection_name

    def _fetch(self, url):
        content = self.fetcher.fetch(url)
        self.storage.save_file(url, content)

        return content

    def _parse_search_results(self, query, search_url):
        content = self.storage.get_file_content(search_url)
        result = self.search_parser.parse(query, content)
        products = result["products"]
        for product in products:
            product["search_url"] = search_url
            self.storage.save(self.collection_name, product)
        return {"search_url": search_url, "products": products}

    def scrape(self, query, num_pages=None, fetch=True):
        futures = []
        pages = []

        with ThreadPoolExecutor(max_workers=self.num_fetch_workers) as executor:
            if num_pages is None:
                num_pages = 1

            for page in range(0, num_pages):
                search_url = self.search_url_templ.format(query, page)
                pages.append(search_url)
                futures.append(executor.submit(
                    self._fetch, url=search_url))

                if page == 0 and as_completed(futures):
                    result = futures[0].result()
                    if num_pages is None:
                        num_pages = ceil(result["num_results"]/64)

        if as_completed(futures):
            futures = []
            with ThreadPoolExecutor(max_workers=self.num_parsing_workers) as executor:
                for page in pages:
                    futures.append(executor.submit(
                        self._parse_search_results, query=query, search_url=page))

        return futures
