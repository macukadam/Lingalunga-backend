import aredis
import os
from lingalunga_server.settings import *

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': os.path.join(BASE_DIR, 'db.sqlite3'),
    }
}

DEBUG = True
redis_client = aredis.StrictRedis(host='127.0.0.1', port=6379)
