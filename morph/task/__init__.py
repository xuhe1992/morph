# -*- coding: utf-8 -*-

"""
@author: xuhe
@date: 17/3/30
@description: 
"""

from celery import Celery
from morph.config import celeryconfig

morph_celery = Celery()
morph_celery.config_from_object(celeryconfig)