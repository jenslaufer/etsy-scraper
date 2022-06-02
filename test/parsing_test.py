
import context
import unittest
from scraper.parser import SearchParser
import requests
import logging


class SearchParserTest(unittest.TestCase):

    def setUp(self) -> None:
        super().setUp()
        logging.basicConfig(level=logging.DEBUG)
        with open("test/resources/search_results.html", "r") as f:
            self.search_results_content = f.read()
        self.search_parser = SearchParser()

    def test_num_of_result(self):
        result = self.search_parser.parse(self.search_results_content)
        self.assertEquals(62573, result["num_of_results"])

    def test_results(self):
        results = self.search_parser.parse(self.search_results_content)
        logging.debug(results)
        self.assertEquals(95, len(results["products"]))
