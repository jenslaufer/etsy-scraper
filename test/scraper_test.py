from asyncio import futures

import context
from unittest import TestCase
from scraper.storage import MongoStorage
from scraper.parser import SearchParser, DetailsParser
from scraper.providers import RequestsFetch, Fetch
from scraper.scraper import Scraper
from pymongo_inmemory import MongoClient as MongoClientInMemory
from concurrent.futures import as_completed


class ScraperTest(TestCase):
    def setUp(self):
        db_name = "test"
        db = MongoClientInMemory()[db_name]

        self.collection_name = "products"
        self.storage = MongoStorage(db)
        self.scraper = Scraper(
            RequestsFetch(),
            self.storage,
            SearchParser(),
            DetailsParser(),
            collection_name=self.collection_name)
        self.query = "programming shirts"
        self.expected_min_props = [
            'title', 'price', 'listing_id', 'url', 'query', 'num_sales', 'shipping_cost']

    def test_scraping(self):
        num_pages = 2
        futures = self.scraper.scrape(
            self.query, num_pages=num_pages)

        self.assertEqual(len(futures), 24)

        if as_completed(futures):
            for future in futures:
                product = future.result()
                listing_id = product["listing_id"]

                stored_product = self.storage.find_by_criteria(
                    self.collection_name, {"listing_id": listing_id})

                product.pop("last_modified_date")

                self.assertTrue(len(product.keys()) > 3)
                self.assertDictContainsSubset(product, stored_product[0])
