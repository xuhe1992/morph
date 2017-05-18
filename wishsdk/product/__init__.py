# -*- coding:utf-8 -*-
import re

__author__ = 'GF'


from datetime import datetime
from wishsdk.connection import Connection
from wishsdk.variant import WishVariant


class WishProduct(Connection):

    def __init__(self, shop):
        Connection.__init__(self)
        self.base_verbs = [
            "product", "product/add", "product/update", "product/enable", "product/disable", "product/multi-get",
            "product/remove-extra-images", "product/create-download-job", "product/get-download-job-status",
            "product/cancel-download-job", "product/get-shipping-setting", "product/get-all-shipping"
        ]
        self.session = shop.session
        self.account = shop.account
        self.shop_id = shop.id
        self.variant_api = WishVariant(shop)

    def retrieve_product_by_id(self, product_id):
        params = {
            "access_token": self.account,
            "id": product_id
        }
        response = self.execute("product", params)
        return response

    def create_product(self, product):
        image = product["variant_image"]
        del product["variant_image"]
        product["main_image"] = re.sub("^https:", "http:", product["main_image"])
        if product.get("extra_images"):
            product["extra_images"] = "|".join([re.sub("^https:", "http:", image)
                                                for image in product["extra_images"].split("|")])
        params = product
        params["access_token"] = self.account
        response = self.execute("product/add", params)
        if response.get("success") and image:
            self.variant_api.update_variant(product["sku"], main_image=image)
        return response

    def update_product_by_id(self, product_id, **kwargs):
        params = {
            "id": product_id,
            "access_token": self.account
        }
        if kwargs.get("main_image"):
            kwargs["main_image"] = re.sub("^https:", "http:", kwargs["main_image"])
        if kwargs.get("variant_image"):
            kwargs["extra_images"] = "|".join([re.sub("^https:", "http:", image)
                                               for image in kwargs["extra_images"].split("|")])
        params.update(kwargs)
        response = self.execute("product/update", params)
        return response

    def enable_product(self, product_id):
        params = {
            "id": product_id,
            "access_token": self.account
        }
        response = self.execute("product/enable", params)
        return response

    def disable_product(self, product_id):
        params = {
            "id": product_id,
            "access_token": self.account
        }
        response = self.execute("product/disable", params)
        return response

    def change_product_state(self, method, product_id):
        """
        enable/disable a product and all of its product variations.
        :return:
        """
        params = {
            "id": product_id,
            "access_token": self.account
        }
        response = self.execute(method, params)
        return response

    def remove_extra_img(self, product_id):
        params = {
            "access_token": self.account,
            "id": product_id
        }
        response = self.execute("product/remove-extra-images", params)
        return response

    def list_all_products(self, start=0, limit=200, since=""):
        params = {
            "access_token": self.account,
            "start": start,
            "limit": limit,
            "since": since,
        }
        if isinstance(since, datetime):
            params["since"] = since.strftime("%Y-%m-%d")
        response = self.execute("product/multi-get", params)
        return response

    def create_download_job(self, since="", limit="", sort=""):
        params = {
            "access_token": self.account,
            "sort": sort,
            "limit": limit,
            "since": since
        }
        if isinstance(since, datetime):
            params["since"] = since.strftime("%Y-%m-%d")
        response = self.execute("product/create-download-job", params)
        return response

    def get_download_job_status(self, job_id):
        params = {
            "access_token": self.account,
            "job_id": job_id
        }
        response = self.execute("product/get-download-job-status", params)
        return response

    def cancel_download_job(self, job_id):
        params = {
            "access_token": self.account,
            "job_id": job_id
        }
        response = self.execute("product/cancel-download-job", params)
        return response

    def get_shipping_setting(self):
        params = {
            "access_token": self.account
        }
        response = self.execute("product/get-shipping-setting", params)
        return response

    def get_all_shipping(self, product_id):
        params = {
            "access_token": self.account,
            "id": product_id
        }
        response = self.execute("product/get-all-shipping", params)
        return response


# from morph.lib.model.shop import Shop
# s = Shop(account="417982669b1f425a977a60ff18106c40")
# response = WishProduct(s).create_download_job()
# print response
# product = WishProduct(s).retrieve_product_by_id("5858e9a1c6897c4efc0c56e0")
# import json
# print json.dumps(product, indent=1)
# pic_url = product["data"]["Product"]["extra_images"].split("|")
# print pic_url
# print len(pic_url)
# products = WishProduct(s).list_all_products()
# print products
# print json.dumps(products["data"], indent=1)
# s = Shop(account="9cf06900688a4e2182b1a30614744ca3")
# job_id = WishProduct(s).create_download_job()["data"]["job_id"]
# import time
# while True:
#     res = WishProduct(s).get_download_job_status(job_id)
#     if res["data"]["status"] == "FINISHED":
#         print res["data"]["download_link"]
#         break
#     else:
#         print "Pending"
#     time.sleep(10)
# import requests
# url = "https://sweeper-production-merchant-export.s3-us-west-1.amazonaws.com/563b3b053a698c01879a8a50-5858f108a1c7061ad830cdda-2016-12-20-08%3A51%3A20.csv?Signature=jUcJOPqv3N5EL9ud6KfnJgFnNJ0%3D&Expires=1482483089&AWSAccessKeyId=AKIAJFT6XO7RY2S4TSRQ"
# res = requests.get(url)
# print res.text

# res = WishProduct(s).get_download_job_status("587497e8c7f90f4f01b71ce4")
# print res