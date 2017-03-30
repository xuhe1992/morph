# -*- coding: utf-8 -*-

# @author: xuhe
# @date: 15/10/27
# @description:


from smtsdk.connection import Connection


class AliPublic(Connection):

    def __init__(self, shop):
        Connection.__init__(self)
        self.base_verbs = [
            "api.queryAeAnouncement", "api.queryServiceAnouncement",
            "api.queryOpenAnouncement"
        ]
        self.session = shop.session
        self.account = shop.account
        self.shop_id = shop.id

    def get_ae_announcement(self, start_time, end_time, page=1):

        params = {
            "access_token": self.account,
            "publicDatetimeStart": start_time,
            "publicDatetimeEnd": end_time,
            "pageSize": 20,
            "page": page
        }
        self.need_signature = True
        response = self.execute("api.queryAeAnouncement", params)
        return response
