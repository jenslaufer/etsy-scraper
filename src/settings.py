# -*- coding: utf-8 -*-

import os
import pymongo

DB_HOST = os.environ.get(
    'MONGODB_HOST')
DB_NAME = os.environ.get(
    'MONGODB_DATABASE')

MONGO_URI = f'mongodb://{DB_HOST}/{DB_NAME}'

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
        'query': {'type': "string", "required": True}
    }
}

products = {
    'schema': {
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
