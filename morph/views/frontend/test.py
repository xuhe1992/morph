# -*- coding: utf-8 -*-

"""
@author: xuhe
@date: 17/3/31
@description: 
"""

from morph.views.base import BaseHandler


class TestHandler(BaseHandler):

    def get(self):
        print self.params
        self.params["a"] = 1
        print self.params
