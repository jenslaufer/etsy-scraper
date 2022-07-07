import os
from scraper.scraper import Scraper
from scraper.providers import RequestsFetch
from scraper.storage import MongoStorage
from scraper.parser import DetailsParser, SearchParser
import logging
from eve import Eve
from concurrent.futures import ThreadPoolExecutor


debug = bool(os.environ.get('DEBUG', "True"))
host = os.environ.get('HOST', '0.0.0.0')
level = int(os.environ.get("LOG_LEVEL", 50))

logging.basicConfig(level=level)

mongo_host = os.environ.get("MONGO_HOST")
mongo_db = os.environ.get("MONGO_DB")

executor = ThreadPoolExecutor(max_workers=10)

app = Eve()

with app.app_context():
    scraper = Scraper(RequestsFetch(), MongoStorage(app.data.driver.db),
                      SearchParser(), DetailsParser())


def _scrape(query, num_pages=None):
    scraper.scrape(query, num_pages)


def insert_scrapes(scrapes):
    for scrape in scrapes:
        executor.submit(_scrape, query=scrape["query"], num_pages=15)


app.on_insert_scrapes += insert_scrapes


if __name__ == "__main__":
    app.run(host=host, debug=debug)
