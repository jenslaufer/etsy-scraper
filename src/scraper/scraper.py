import logging
import random
import time
import urllib.parse
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import date, datetime, timedelta
from math import ceil

from scraper.parser import DetailsParser, SearchParser
from scraper.providers import Fetch
from scraper.storage import Storage
from urllib import parse


class Scraper:

    def __init__(self, fetcher: Fetch, storage: Storage,
                 search_parser: SearchParser,
                 details_parser: DetailsParser,
                 collection_name="products",
                 num_fetch_workers=10, num_parsing_workers=50):
        super().__init__()

        self.storage = storage
        self.search_parser = search_parser
        self.details_parser = details_parser
        self.fetcher = fetcher
        self.search_url_templ = "https://www.etsy.com/de/search?q={}&page={}&ref=pagination"
        self.details_url_templ = "https://www.etsy.com/de/listing/{}"
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
        """ for product in products:
            product["search_url"] = search_url
            self.storage.save(self.collection_name, product) """
        return {"search_url": search_url, "products": products}

    def _merge_details(self, product, details_url):
        content = self.fetcher.fetch(details_url)
        self.storage.save_file(details_url, content, doc_type="details")
        try:
            product_details = self.details_parser.parse(
                product["listing_id"], content)
            merged_product = {**product, **product_details}

            today = datetime.combine(date.today(), datetime.min.time())
            tomorrow = today + timedelta(days=1)

            self.storage.replace(self.collection_name, {
                "listing_id": merged_product["listing_id"],
                "last_modified_date": {"$gte": today, "$lt": tomorrow}}, merged_product)

            return merged_product
        except Exception as e:
            logging.error(f"could get details: {e}")

    def scrape(self, scraping_id, query, num_pages=None, fetch=True):
        futures = []
        pages = []

        with ThreadPoolExecutor(max_workers=self.num_fetch_workers) as executor:
            if num_pages is None:
                num_pages = 1

            for page in range(1, num_pages+1):
                search_url = self.search_url_templ.format(
                    parse.quote(query.encode('utf8')), page)
                pages.append(search_url)
                futures.append(executor.submit(
                    self._fetch, url=search_url))

                if page == 1 and as_completed(futures):
                    result = futures[0].result()
                    if num_pages is None:
                        num_pages = ceil(result["num_results"]/64)

        if as_completed(futures):
            parsings = []
            with ThreadPoolExecutor(max_workers=self.num_parsing_workers) as executor:
                for page in pages:
                    parsings.append(executor.submit(
                        self._parse_search_results, query=query, search_url=page))

        if as_completed(parsings):
            details = []
            with ThreadPoolExecutor(max_workers=self.num_fetch_workers) as executor:
                for parsing in parsings:
                    products = parsing.result()["products"]
                    for product in products:
                        product["scraping_id"] = scraping_id
                        details_url = self.details_url_templ.format(
                            product["listing_id"])
                        details.append(executor.submit(
                            self._merge_details, product=product, details_url=details_url))

        return details
