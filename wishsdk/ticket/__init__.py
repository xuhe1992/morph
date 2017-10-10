# -*- coding: utf-8 -*-

# @author: xuhe
# @date: 15/12/28
# @description:

from morph.lib.model.shop import Shop
from wishsdk.connection import Connection


class WishTicket(Connection):

    def __init__(self, shop):
        Connection.__init__(self)
        self.base_verbs = [
            "ticket", "ticket/get-action-required", "ticket/reply",
            "ticket/close", "ticket/appeal-to-wish-product", "ticket/re-open"
        ]
        self.session = shop.session
        self.account = shop.account
        self.shop_id = shop.id

    def retrieve_ticket_by_id(self, ticket_id):
        params = {
            "access_token": self.account,
            "id": ticket_id
        }
        response = self.execute("ticket", params)
        return response

    def list_all_tickets(self, start=0, limit=500):
        params = {
            "access_token": self.account,
            "start": start,
            "limit": limit
        }
        response = self.execute("ticket/get-action-required", params)
        return response

    def close_ticket_by_id(self, ticket_id):
        params = {
            "access_token": self.account,
            "id": ticket_id
        }
        response = self.execute("ticket/close", params)
        return response

    def reply_ticket_by_id(self, ticket_id, reply):
        params = {
            "access_token": self.account,
            "id": ticket_id,
            "reply": reply
        }
        response = self.execute("ticket/reply", params)
        return response

    def appeal_support_ticket_by_id(self, ticket_id):
        params = {
            "access_token": self.account,
            "id": ticket_id
        }
        response = self.execute("ticket/appeal-to-wish-product", params)
        return response

    def open_ticket_by_id(self, ticket_id, reply):
        params = {
            "access_token": self.account,
            "id": ticket_id,
            "reply": reply
        }
        response = self.execute("ticket/re-open", params)
        return response


m = {
    u'code': 0,
    u'data': {
        u'Ticket': {
            u'UserInfo': {
                u'id': u'123456789012345678901234',
                u'joined_date': u'2012-02-02T11:22:21',
                u'locale': u'en',
                u'name': u'George Forman'
            },
            u'close_date': u'2015-03-08T22:31:02',
            u'closed_by': u'wish support',
            u'id': u'123456789012345678901234',
            u'items': [{
                u'Order': {
                    u'ShippingDetail': {
                        u'city': u'',
                        u'country': u'US',
                        u'name': u'George Forman',
                        u'phone_number': u'123456',
                        u'state': u'California',
                        u'street_address1': u'123 Fake St',
                        u'zipcode': u'11111'
                    },
                    u'buyer_id': u'123456789012345678901234',
                    u'cost': u'6.69',
                    u'last_updated': u'2011-03-08T22:31:02',
                    u'order_id': u'123456789012345678901234',
                    u'order_time': u'2015-02-20T02:55:27',
                    u'order_total': u'9.39',
                    u'price': u'6.4',
                    u'product_id': u'123456789012345678901234',
                    u'product_image_url': u'https://google.com/not-a-image',
                    u'product_name': u'A product',
                    u'quantity': u'1',
                    u'refunded_by': u'REFUNDED BY WISH FOR MERCHANT',
                    u'refunded_reason': u'Item did not work as described',
                    u'refunded_time': u'2015-03-18',
                    u'shipped_date': u'2015-02-20',
                    u'shipping': u'3.0',
                    u'shipping_cost': u'2.7',
                    u'shipping_provider': u'USPS',
                    u'sku': u'SKU123',
                    u'state': u'REFUNDED',
                    u'tracking_number': u'TR1234ACK',
                    u'transaction_id': u'1223456789012345678901234',
                    u'variant_id': u'123456789012345678901234'
                }
            }],
            u'label': u'Return or Exchange',
            u'last_update_date': u'2015-02-09T12:13:43',
            u'merchant_id': u'123456789012345678901234',
            u'open_date': u'2015-03-06T21:23:01',
            u'photo_proof': u'True',
            u'replies': [{
                u'Reply': {
                    u'date': u'2015-03-06T21:23:01',
                    u'image_urls': u"[u'https://fake-url']",
                    u'message': u"Where is my product?",
                    u'sender': u'user',
                    u'translated_message': u"Where is my product?",
                    u'translated_message_zh': u'\u54EA\u91CC\u662F\u6211\u7684\u4EA7\u54C1\uFF1F'
                }
            }],
            u'state': u'Awaiting your response',
            u'state_id': u'1',
            u'subject': u'Return or Exchange',
            u'sublabel': u'',
            u'transaction_id': u'123456789012345678901234'
        }
    },
    u'message': u''
}

if __name__ == "__main__":
    shop = Shop()
    shop.account = "373756ae5115474c8f0bcba44159194a"
    shop.session = "f5d42d3b104c4043859e09785e573e05"
    shop.owner = "596d75982eac1176e8290607"
    shop.platform = "Wish"
    shop.id = 15183
    shop.site_id = 1

    hanler = WishTicket(shop)

    # result = hanler.list_all_tickets()
    #
    # import json
    # print json.dumps(result, indent=2)

