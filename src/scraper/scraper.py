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

    def _fetch(self, url, ref):
        content = self.fetcher.fetch(url)
        self.storage.save_file(url, content, ref=ref)

        return {"content": content, "search_url": url, "scraping_id": ref}

    def _parse_search_results(self, query, result):
        content = result["content"]
        scraping_id = result["scraping_id"]
        result = self.search_parser.parse(
            query, scraping_id, content)
        products = result["products"]
        return products

    def _merge_details(self, product, details_url, ref):
        content = self.fetcher.fetch(details_url)
        self.storage.save_file(details_url, content,
                               doc_type="details", ref=ref)
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

        with ThreadPoolExecutor(max_workers=self.num_fetch_workers) as executor:
            if num_pages is None:
                num_pages = 1

            for page in range(1, num_pages+1):
                search_url = self.search_url_templ.format(
                    parse.quote(query.encode('utf8')), page)
                futures.append(executor.submit(
                    self._fetch, url=search_url, ref=scraping_id))

                # if page == 1 and as_completed(futures):
                #     result = futures[0].result()
                #     if num_pages is None:
                #         num_pages = ceil(result["num_results"]/64)

        if as_completed(futures):
            parsings = []
            with ThreadPoolExecutor(max_workers=self.num_parsing_workers) as executor:
                for future in futures:
                    result = future.result()
                    parsings.append(executor.submit(
                        self._parse_search_results, query=query, result=result))

        if as_completed(parsings):
            details = []
            with ThreadPoolExecutor(max_workers=self.num_fetch_workers) as executor:
                for parsing in parsings:
                    products = parsing.result()
                    for product in products:
                        if product.get("listing_id") != None:
                            details_url = product.get("url")
                            details.append(executor.submit(
                                self._merge_details, product=product, details_url=details_url, ref=scraping_id))
            if as_completed(details):
                return details
