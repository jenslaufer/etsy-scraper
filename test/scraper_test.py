from asyncio import futures
import context
from unittest import TestCase
from scraper.storage import MongoStorage
from scraper.parser import SearchParser
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
            collection_name=self.collection_name)
        self.query = "programming shirts"

    def test_scraping(self):
        num_pages = 2
        futures = self.scraper.scrape(
            self.query, num_pages=num_pages)

        self.assertEquals(num_pages, len(futures))
        if as_completed(futures):
            for future in futures:
                result = future.result()
                products = result["products"]
                search_url = result["search_url"]

                self.assertTrue(self.storage.exists(search_url))
                self.assertTrue(
                    "html" in self.storage.get_file_content(search_url).decode("utf-8"))
                self.assertTrue(len(products) > 1)
                for product in products:
                    url = product["url"]
                    data = self.storage.find_by_criteria(
                        self.collection_name, {"url": url})

                    self.assertEqual(data[0]["url"], url)
