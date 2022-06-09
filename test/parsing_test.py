
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
        self.query = "test"

    def test_num_of_result(self):
        result = self.search_parser.parse(
            self.query, self.search_results_content)
        self.assertEquals(62573, result["num_of_results"])

    def test_results(self):

        results = self.search_parser.parse(
            self.query, self.search_results_content)
        logging.debug(results)
        self.assertEquals(self.query, results["products"][1]["query"])
        self.assertEquals(
            "Personal Trainer Program Template Forms BUNDLE / Measurement Forms / Food Journal / Google Sheets /  Fitness Instructor Programming", results["products"][1]["title"])
        self.assertEquals(26.74, results["products"][1]["price"])
        self.assertEquals(4.8537, results["products"][1]["rating"])
        self.assertEquals(41, results["products"][1]["num_ratings"])
        self.assertEquals(1174291147, results["products"][1]["listing_id"])
        self.assertEquals(
            "https://www.etsy.com/listing/1174291147/", results["products"][1]["url"])
