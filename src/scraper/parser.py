import os
from lxml import html, etree
import logging
from math import ceil
import re
import logging


class Parser:
    def parse(self, query, content) -> dict:
        pass


class SearchParser(Parser):

    def __init__(self):
        super().__init__()
        self.num_regex = r"[0-9\.\,]+"

    def _num_results(self, doc):
        results_xpath = ".//span[@class = 'wt-display-inline-flex-sm']/span/text()"
        num_of_results = 0
        try:
            num_results_str = doc.xpath(results_xpath)[0]
            num_of_results = int(re.findall(self.num_regex, num_results_str)[
                0].replace(".", ""))

        except Exception as e:
            logging.debug(f"could not extract results: {e}")

        return num_of_results

    def _products(self, query, doc):
        products = []
        products_xpath = ".//li[contains(@class,'wt-list-unstyled')]"
        title_xpath = ".//a/@title"
        price_xpath = ".//span[@class='currency-value']/text()"
        rating_xpath = ".//input[@name='rating']/@value"
        num_ratings_xpath = ".//span[contains(@class,'wt-text-body-01')]/text()"
        listing_id_xpath = ".//div[@data-listing-id]/@data-listing-id"

        for product_section in doc.xpath(products_xpath):
            product = {}
            try:
                title = product_section.xpath(title_xpath)[0].strip()
                product["title"] = title
            except Exception as e:
                logging.warning(f"Could not extract title: {e}")

            try:
                price = float(product_section.xpath(price_xpath)
                              [0].strip().replace(",", "."))
                product["price"] = price
            except Exception as e:
                logging.warning(f"Could not extract currency: {e}")

            try:
                rating = float(product_section.xpath(rating_xpath)[0].strip())
                product['rating'] = rating
            except Exception as e:
                logging.warning(f"could not extract rating: {e}")

            try:
                num_rating_str = product_section.xpath(
                    num_ratings_xpath)[0].strip().replace(".", "")

                num_ratings = int(re.findall(
                    self.num_regex, num_rating_str)[0])
                product['num_ratings'] = num_ratings
            except Exception as e:
                logging.warning(f"could not extract rating: {e}")

            try:
                listing_id = int(product_section.xpath(listing_id_xpath)[0])
                product["listing_id"] = listing_id
                product["url"] = f"https://www.etsy.com/listing/{listing_id}/"
            except Exception as e:
                logging.warning(f"could not extract listing_id: {e}")

            if len(product.keys()) > 0:
                product["query"] = query
                products.append(product)

        return products

    def parse(self, query, content) -> dict:
        doc = html.fromstring(content)
        num_of_results = self._num_results(doc)
        products = self._products(query, doc)

        return {"num_of_results": num_of_results, "products": products}


class DetailsParser(Parser):
    def __init__(self) -> None:
        super().__init__()
        self.num_regex = r"[0-9\.\,]+"

    def parse(self, listing_id, content) -> dict:
        doc = html.fromstring(content)

        num_sales = 0
        try:
            num_sales_xpath = ".//span[@class = 'wt-text-caption']/text()"
            num_sales_str = doc.xpath(num_sales_xpath)[0]
            num_sales = int(re.findall(self.num_regex, num_sales_str)[
                            0].replace(".", ""))
        except Exception as e:
            logging.warning(f"could not extract num_sales: {e}")

        return {"listing_id": listing_id, "num_sales": num_sales}
