import os
from lingalunga_server.settings import *
import redis.asyncio as redis

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': os.path.join(BASE_DIR, 'db.sqlite3'),
    }
}

DEBUG = True

redis_pool = redis.ConnectionPool(
    host='localhost', port=6379, db=0, max_connections=10)
