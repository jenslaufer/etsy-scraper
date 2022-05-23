import os
from lxml import html, etree
import logging
from math import ceil
import re


class SearchParser:

    def __init__(self):
        super().__init__()

    def parse(self, content):
        doc = html.fromstring(content)
        return {}
