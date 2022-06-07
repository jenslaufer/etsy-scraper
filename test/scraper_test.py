import context
from unittest import TestCase
from scraper.storage import MongoStorage
from scraper.parser import SearchParser
from scraper.providers import RequestsFetch, Fetch
from scraper.scraper import Scraper
from pymongo_inmemory import MongoClient


class ScraperTest(TestCase):
    def setUp(self):
        db = MongoClient()["test"]
        self.storage = MongoStorage(db)
        self.scraper = Scraper(
            RequestsFetch(),
            self.storage,
            SearchParser())

    def test_scraping(self):
        num_pages = 2
        pages = self.scraper.scrape("programming shirts", num_pages=num_pages)
        self.assertEquals(num_pages, len(pages))
        for page in pages:
            self.assertTrue(self.storage.exists(page))
            self.assertTrue(
                "html" in self.storage.get_file_content(page).decode("utf-8"))
