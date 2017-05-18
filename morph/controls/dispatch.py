# -*- coding: utf-8 -*-

"""
@author: xuhe
@date: 17/3/31
@description: 
"""

from morph.controls.ebay.sync import SyncEbayCustomer
from morph.controls.smt.sync import SyncSmtCustomer
from morph.controls.wish.sync import SyncWishCustomer


class CustomerDispatch(object):

    def __init__(self, platform, **params):
        self.platform = platform
        self.params = params

    def execute(self):
        method_route = {
            "AliExpress": SyncSmtCustomer,
            "eBay": SyncEbayCustomer,
            "Wish": SyncWishCustomer,
        }
        method_route[self.params]()



