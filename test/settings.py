# -*- coding: utf-8 -*-

import os
import pymongo
import logging

MONGO_URI = f'mongodb://localhost/bookings'
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


bookings = {
    'schema': {
        'name': {"type": "string", 'required': True},
        'status': {'type': 'string', 'allowed': ['CREATED', 'PROCESSED', 'ERROR']}
    }

}

DOMAIN = {
    'bookings': bookings
}
