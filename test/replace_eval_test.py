from sympy import O
import context
from unittest import TestCase
from pymongo_inmemory import MongoClient as MongoClientInMemory
from scraper.storage import MongoStorage
from datetime import datetime, timedelta, date


class MongoStorageReplaceEvalTest(TestCase):

    def setUp(self):
        db_name = "test"
        db = MongoClientInMemory()[db_name]
        self.storage = MongoStorage(db)
        self.listing_id = 498984760285

        self.data = {'listing_id': self.listing_id, "prop": "blub",
                     'last_modified_date': datetime.utcnow()}
        self.storage.save("test", self.data)

    def tearDown(self) -> None:
        self.storage.remove("test", {"listing_id": self.listing_id})

    def test_replace_same_day(self):

        data = {"listing_id": self.listing_id, "prop": "blubb",
                'last_modified_date': datetime.utcnow()}
        today = datetime.combine(date.today(), datetime.min.time())
        tomorrow = today + timedelta(days=1)
        criteria = {"listing_id": self.listing_id, "last_modified_date": {
            "$gte": today, "$lt": tomorrow}}
        print(f"criteria: {criteria}")

        self.storage.replace("test", criteria, data)

        results = self.storage.find_by_criteria("test")

        self.assertEqual(len(results), 1)
        self.assertEqual(results[0]["prop"], "blubb")

    def test_replace_next_day(self):

        data = {"listing_id": self.listing_id, "prop": "blubb",
                'last_modified_date': datetime.utcnow()}
        yesterday = datetime.combine(
            date.today(), datetime.min.time()) - timedelta(days=1)
        today = yesterday + timedelta(days=1)
        criteria = {"listing_id": self.listing_id, "last_modified_date": {
            "$gte": yesterday, "$lt": today}}
        print(f"criteria: {criteria}")

        self.storage.replace("test", criteria, data)

        results = self.storage.find_by_criteria("test")

        self.assertEqual(len(results), 2)
        self.assertEqual(results[0]["prop"], "blub")
        self.assertEqual(results[1]["prop"], "blubb")
