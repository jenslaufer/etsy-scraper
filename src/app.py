from asyncio import as_completed
import os
from scraper.scraper import Scraper
from scraper.providers import RequestsFetch
from scraper.storage import MongoStorage
from scraper.parser import DetailsParser, SearchParser
import logging
from eve import Eve
from concurrent.futures import ThreadPoolExecutor
from scrpproxies.proxy import MultipleIpProxy


debug = bool(os.environ.get('DEBUG', "True"))
host = os.environ.get('HOST', '0.0.0.0')
level = int(os.environ.get("LOG_LEVEL", 50))
num_fetch_workers = int(os.environ.get("NUM_SCRAPING_WORKERS", 50))

logging.basicConfig(level=level)

executor = ThreadPoolExecutor(max_workers=10)

app = Eve()

proxies = MultipleIpProxy("proxylist.csv")

logging.debug(
    f"num_fetch_workers: {num_fetch_workers}, proxy_ip: {proxies.get()}")

with app.app_context():
    storage = MongoStorage(app.data.driver.db)
    scraper = Scraper(RequestsFetch(), storage,
                      SearchParser(), DetailsParser(),
                      num_fetch_workers=num_fetch_workers)


def done_callback(future):
    scrape = future.result()
    scrape["status"] = "PROCESSED"
    storage.replace("scrapes", {"_id": scrape["_id"]}, scrape)


def _scrape(scrape, num_pages=None):
    query = scrape["query"]
    scraper.scrape(query, num_pages)

    return scrape


def inserted_scrapes(scrapes):
    for scrape in scrapes:
        future = executor.submit(_scrape, scrape=scrape, num_pages=10)
        future.add_done_callback(done_callback)


def insert_scrapes(scrapes):
    for scrape in scrapes:
        scrape["status"] = "CREATED"


app.on_insert_scrapes += insert_scrapes
app.on_inserted_scrapes += inserted_scrapes


if __name__ == "__main__":
    app.run(host=host, debug=debug)
