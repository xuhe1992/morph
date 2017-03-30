#coding=utf8

import datetime
from furion.lib.model.shop import Shop
from furion.lib.utils.logger_util import logger

__author__ = 'Administrator'

from smtsdk.connection import Connection


class AliTrade(Connection):

    def __init__(self, shop):
        Connection.__init__(self)
        self.base_verbs = [
            "api.findOrderTradeInfo", "api.findOrderReceiptInfo",
            "api.findOrderBaseInfo", "api.findOrderListSimpleQuery",
            "api.requestPaymentRelease", "api.updateDeliveriedConfirmationFile",
            "api.findLoanListQuery", "api.findOrderById",
            "api.findOrderListQuery"
        ]
        self.account = shop.account
        self.session = shop.session
        self.shop_id = shop.id

    def get_orders_list(self, search_time, create_time_from, create_time_to, numbers_of_days, order_status, page):
        if numbers_of_days:
            time_begin = search_time - datetime.timedelta(days=int(numbers_of_days))
            time_end = search_time
        else:
            time_begin = create_time_from
            time_end = create_time_to

        params = {
            "access_token": self.account,
            "page": page,
            "pageSize": 50,
            "orderStatus": order_status,
            "createDateStart": time_begin,
            "createDateEnd": time_end
        }
        logger.info("++++++++++++++++++++++++")
        logger.info(params)
        self.need_signature = True

        response = self.execute('api.findOrderListQuery', params)
        return response

    def get_order_detail_by_id(self, order_id):

        params = {
            "access_token": self.account,
            'orderId': order_id
        }
        self.need_signature = True

        response = self.execute('api.findOrderById', params)
        return response

    def get_orders_list_all(self, page=1):
        params = {
            # "orderStatus": "RISK_CONTROL",
            "access_token": self.account,
            "page": page,
            "pageSize": 50,
        }
        self.need_signature = True

        response = self.execute('api.findOrderListQuery', params)
        return response

    def get_orders_simple_list(self, page=1):
        params = {
            "access_token": self.account,
            "page": page,
            "pageSize": 50,
            "orderStatus": "FINISH"
        }
        self.need_signature = True
        response = self.execute('api.findOrderListQuery', params)
        return response

#
if __name__ == "__main__":
    shop = Shop()
    shop.account = "0e6d6295-33ef-4dba-acbe-f81ad2c08fb2"
    shop.session = "997bb82d-22e7-4947-a235-d1ea53c242f2"
    AT = AliTrade(shop)
    res1 = AT.get_orders_list_all(page=1)
    print res1


    # print res1
    # res2 = AT.get_order_detail_by_id(72225047485505)
    # print res2