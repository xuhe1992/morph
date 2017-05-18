# -*- coding: utf-8 -*-

"""
@author: xuhe
@date: 17/3/30
@description: 
"""

import os
from morph.config.base import *


# mongo configure
MONGO_HOST = '230.actneed.com'
MONGO_PORT = 37017
MAX_POOL_SIZE = 20

# log configure
LOG_PATH = '/home/kratos/log/hades'
LOG_FILE = os.path.sep.join([LOG_PATH, 'hades.log'])
DEFAULT_LOG_SIZE = 1024*1024*50

# mysql configure
ECHO_SQL = False
DB = {
    "user": "kratos",
    "password": "3vUbY52IJ2fJq7KwWPeItNrz8",
    "host": "230.actneed.com",
    "db_name": "fr",
}

# YAML configure
EBAY_YAML = "/home/kratos/src/morph_current/ebay.yaml"
ALI_YAML = "/home/kratos/src/morph_current/ali.yaml"
AMAZON_YAML = "/home/kratos/src/morph_current/amazon.yaml"
WISH_YAML = "/home/kratos/src/morph_current/wish.yaml"

# redis configure
REDIS_HOST = "230.actneed.com"
REDIS_PORT = 6363
REDIS_DB = 0
REDIS_PASSWORD = "n1UUi4IKc1m2hV277eZtYW9T451p5lV3tSHAFJ647Xai83U44izwm2ciXDrxt05p"
REDIS_MAX_CONNECTIONS = 50

# api secret key
API_KEY = "ActNeed#HADES#SeRVeR#API$KeY$"