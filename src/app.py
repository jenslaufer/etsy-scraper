import os
from scraper.scraper import Scraper
from scraper.providers import RequestsFetch
from scraper.storage import MongoStorage
from scraper.parser import DetailsParser, SearchParser
import logging

from eve import Eve


debug = bool(os.environ.get('DEBUG', "True"))
host = os.environ.get('HOST', '0.0.0.0')
level = int(os.environ.get("LOG_LEVEL", 50))

logging.basicConfig(level=level)

mongo_host = os.environ.get("MONGO_HOST")
mongo_db = os.environ.get("MONGO_DB")

app = Eve()

with app.app_context():
    scraper = Scraper(RequestsFetch(), MongoStorage(app.data.driver.db),
                      SearchParser(), DetailsParser())

if __name__ == "__main__":
    app.run(host=host, debug=debug)
