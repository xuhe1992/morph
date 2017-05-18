# -*- coding: utf-8 -*-

"""
@author: xuhe
@date: 17/3/31
@description: 
"""

import re
import ujson as json
from morph.controls.amazon import AmazonCustomer
from morph.controls.ebay import EbayCustomer
from morph.controls.smt import SmtCustomer
from morph.controls.wish import WishCustomer
from morph.lib.utils.exc import MissArgumentError
from morph.views.base import BaseHandler


class CustomerHandler(BaseHandler):

    controls_map = {
        "AliExpress": SmtCustomer,
        "Amazon": AmazonCustomer,
        "eBay": EbayCustomer,
        "Wish": WishCustomer,
    }

    def get(self, *args, **kwargs):
        logger_dict = {"args": args, "kwargs": kwargs, "params": self.params, "method": "GET"}
        pass

    def post(self, *args, **kwargs):
        logger_dict = {"args": args, "kwargs": kwargs, "params": self.params, "method": "POST"}
        method_route = {
            "sync": self.sync_customer,
        }

    def sync_customer(self):
        self.check_params("sync")
        pass

    def check_params(self, route):
        dic = {
            "sync": {
                "shop_id": "#@\d+",
                "platform": "#@\d+",
            }
        }
        for key, value in dic[route].items():
            command, expression = value.split("@")
            if command == "#" and not self.params.get(key):
                continue
            elif command == "$":
                try:
                    json.loads(self.params.get(key))
                except (ValueError, TypeError):
                    raise MissArgumentError
            else:
                pattern = re.compile(value.strip("#"))
                if not pattern.match(self.params.get(key, "")):
                    raise MissArgumentError