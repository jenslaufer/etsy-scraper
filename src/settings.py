# -*- coding: utf-8 -*-

import os
import pymongo
import logging

DB_HOST = os.environ.get(
    'MONGODB_HOST')
DB_NAME = os.environ.get(
    'MONGODB_DATABASE')

MONGO_URI = f'mongodb://{DB_HOST}/{DB_NAME}'
logging.debug(MONGO_URI)


PAGINATION_LIMIT = 10
PAGINATION_DEFAULT = 5

RESOURCE_METHODS = ['POST', 'GET']

ITEM_METHODS = ['GET', 'PATCH', 'PUT', "DELETE"]

CACHE_CONTROL = 'max-age=20'
CACHE_EXPIRES = 20

X_DOMAINS = '*'
X_HEADERS = ['Content-Type', 'Authorization', 'If-Match']

EXTRA_RESPONSE_FIELDS = ["runtime"]


scrapes = {
    'schema': {
        'query': {'type': "string", "required": True},
        'status': {'type': 'string', 'allowed': ['CREATED', 'PROCESSED', 'ERROR']}
    }
}

products = {
    'schema': {
        'scraping_id': {"type": "string"},
        'listing_id': {"type": "string"},
        'num_sales': {"type": "integer"},
        'shipping_cost': {"type": "float"},
        'title': {"type": "string"},
        'price': {"type": 'float'},
        'currency': {"type": "string"},
        'rating': {'type': 'float'},
        'num_ratings': {'type': 'integer'},
        'query': {"type": "string"},
    }

}


DOMAIN = {
    'scrapes': scrapes,
    'products': products
}
