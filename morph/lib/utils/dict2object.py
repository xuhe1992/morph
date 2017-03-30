#! -*- coding=utf-8 -*-

"""
@author:Xuhe
@version:1.0
@date:14-8-8
"""


class Dict2Obj(object):
    """
    将dict转换为DictObj对象

    """
    def __init__(self, d):
        if isinstance(d, dict):
            for k, v in d.items():
                self.__setattr__(k, v)

    def configure(self, key, value):
        self.__setattr__(key.lower(), value)