import os
from lxml import html, etree
import logging
from math import ceil
import re


class SearchParser:

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

    def _products(self, doc):
        products = []
        products_xpath = ".//li"
        title_xpath = ".//a/@title"
        price_xpath = ".//span[@class='currency-value']"
        for product_section in doc.xpath(products_xpath):
            product = {}
            try:
                title = product_section.xpath(title_xpath)[0].strip()
                product["title"] = title
            except Exception as e:
                logging.warning("Could not extract title")
            try:
                title = product_section.xpath(title_xpath)[0].strip()
                product["title"] = title
            except Exception as e:
                logging.warning("Could not extract title")

            products.append(product)

        return products

    def parse(self, content):
        doc = html.fromstring(content)
        num_of_results = self._num_results(doc)
        products = self._products(doc)
        return {"num_of_results": num_of_results, "products": products}
