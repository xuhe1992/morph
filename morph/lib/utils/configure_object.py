# -*- coding: utf-8 -*-

"""
@author: xuhe
@date: 17/1/16
@description:
"""


def dict_from_model(model):
    setting = {}
    for key in dir(model):
        if key.isupper():
            setting[key.lower()] = getattr(model, key)
    return setting