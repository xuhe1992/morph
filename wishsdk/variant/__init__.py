# -*- coding:utf-8 -*-
import re

__author__ = 'GF'


from wishsdk.connection import Connection


class WishVariant(Connection):

    def __init__(self, shop):
        Connection.__init__(self)
        self.base_verbs = [
            "variant", "variant/add", "variant/update", "variant/enable", "variant/disable", "variant/update-inventory",
            "variant/multi-get"
        ]
        self.session = shop.session
        self.account = shop.account
        self.shop_id = shop.id

    def create_variant(self, variant):
        if variant.get("main_image"):
            variant["main_image"] = re.sub("^https:", "http:", variant["main_image"])
        variant["access_token"] = self.account
        response = self.execute("variant/add", variant)
        return response

    def retrieve_variant(self, sku):
        params = {
            "sku": sku,
            "access_token": self.account
        }
        response = self.execute("variant", params)
        return response

    def update_variant(self, sku, **kwargs):
        params = {
            "sku": sku,
            "access_token": self.account
        }
        if kwargs.get("main_image"):
            kwargs["main_image"] = re.sub("^https:", "http:", kwargs["main_image"])
        params.update(kwargs)
        response = self.execute("variant/update", params)
        return response

    def enable_variant(self, sku):
        params = {
            "sku": sku,
            "access_token": self.account
        }
        response = self.execute("variant/enable", params)
        return response

    def disable_variant(self, sku):
        params = {
            "sku": sku,
            "access_token": self.account
        }
        response = self.execute("variant/disable", params)
        return response

    def update_inventory(self, inventory, sku):
        params = {
            "sku": sku,
            "inventory": inventory,
            "access_token": self.account
        }
        response = self.execute("variant/update-inventory", params)
        return response

    def list_all_variants(self, start, limit):
        params = {
            "access_token": self.account,
            "start": start,
            "limit": limit
        }
        response = self.execute("variant/multi-get", params)
        return response