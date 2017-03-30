# -*- coding:utf-8 -*-


__author__ = 'GF'

from wishsdk.connection import Connection


class WishOrder(Connection):

    def __init__(self, shop):
        Connection.__init__(self)
        self.base_verbs = [
            "order", "order/multi-get", "order/get-fulfill", "order/fulfill-one", "order/refund",
            "order/modify-tracking", "order/change-shipping"
        ]
        self.account = shop.account
        self.session = shop.session
        self.shop_id = shop.id

    def retrieve_order_by_id(self, order_id):
        params = {
            "access_token": self.account,
            "id": order_id
        }
        response = self.execute("order", params)
        return response

    def retrieve_recently_changed_orders(self, start, since=None):
        params = {
            "access_token": self.account,
            "start": start,
            "limit": 500
        }
        if since:
            params["since"] = since
        response = self.execute("order/multi-get", params)
        return response

    def retrieve_unfulfilled_orders(self, start, since):
        params = {
            "access_token": self.account,
            "start": start,
            "limit": 500
        }
        response = self.execute("order/get-fulfill", params)
        return response

    def fulfill_order(self, order_id, tracking_provider, tracking_number, ship_note=""):
        params = {
            "access_token": self.account,
            "id": order_id,
            "tracking_provider": tracking_provider,
            "tracking_number": tracking_number,
            "ship_note": ship_note
        }
        response = self.execute("order/fulfill-one", params)
        return response

    def cancel_order(self, order_id, reason_code, reason_note=""):
        params = {
            "access_token": self.account,
            "id": order_id,
            "reason_code": reason_code,
            "reason_note": reason_note
        }
        response = self.execute("order/refund", params)
        return response

    def change_shipping(self, order_id, address1, address2, city, state, zipcode, country, phone_number):
        params = {
            "access_token": self.account,
            "id": order_id,
            "street_address1": address1,
            "street_address2": address2,
            "city": city,
            "state": state,
            "zipcode": zipcode,
            "country": country,
            "phone_number": phone_number
        }
        response = self.execute("order/change-shipping", params)
        return response

    def modify_order_tracking(self, order_id, tracking_provider, tracking_number, ship_note=""):
        params = {
            "access_token": self.account,
            "id": order_id,
            "tracking_provider": tracking_provider,
            "tracking_number": tracking_number,
            "ship_note": ship_note
        }
        response = self.execute("order/modify-tracking", params)
        return response
# #
# from furion.lib.model.shop import Shop
# shop = Shop()
# shop.account = "acc850109f764b41bcf7fa2fe4747628"
# shop.session = "9151a8f84fca4714a67c09637bd19b09"
# wo = WishOrder(shop)
# # z = wo.retrieve_recently_changed_orders("20", "2016-07-04T20:10:20")
# z = wo.retrieve_unfulfilled_orders(0,0)
# print z
# print len(z["data"])