# -*- coding: utf-8 -*-

"""
@author: xuhe
@date: 17/3/30
@description: 
"""

import os
from morph.config.base import *


# mongo configure
MONGO_HOST = '194.actneed.com'
MONGO_PORT = 27017
MAX_POOL_SIZE = 20

# log configure
LOG_PATH = '/tmp/'
LOG_FILE = os.path.sep.join([LOG_PATH, 'hades.log'])
DEFAULT_LOG_SIZE = 1024*1024*50

# mysql configure
ECHO_SQL = False

DB = {
    "user": "root",
    "password": "qZeEg43S34j3wzMW89MUPcOSS",
    "host": "194.actneed.com",
    "db_name": "fr",
}

# YAML configure
# EBAY_YAML = "/Users/xuhe/PyCharmProjects/Morph/ebay.yaml"
EBAY_YAML = "/home/kratos/src/morph_current/ebay.yaml"
ALI_YAML = "/home/kratos/src/morph_current/ali.yaml"
AMAZON_YAML = "/home/kratos/src/morph_current/amazon.yaml"
WISH_YAML = "/home/kratos/src/morph_current/wish.yaml"

# redis configure
REDIS_HOST = "194.actneed.com"
REDIS_HOST2 = "194.actneed.com"
REDIS_PORT = 6379
REDIS_DB = 0
REDIS_PASSWORD = "n1UUi4IKc1m2hV277eZtYW9T451p5lV3tSHAFJ647Xai83U44izwm2ciXDrxt05p"
REDIS_MAX_CONNECTIONS = 1024

# api secret key
API_KEY = "ActNeed#HADES#SeRVeR#API$KeY$"