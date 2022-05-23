import os
from scraper.scraper import Scraper
from scraper.providers import RequestsFetch
from scraper.storage import MongoStorage
from scraper.parser import SearchParser
from pymongo import MongoClient

mongo_host = os.environ.get("MONGO_HOST")
mongo_db = os.environ.get("MONGO_DB")

print(mongo_host)
print(mongo_db)

db = MongoClient(f"mongodb://{mongo_host}")[mongo_db]

scraper = Scraper(RequestsFetch(), MongoStorage(db), SearchParser())
scraper.scrape("programming", fetch=True)
