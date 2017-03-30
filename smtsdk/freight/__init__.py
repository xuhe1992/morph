# -*- coding: utf-8 -*-

# @author: xuhe
# @date: 15/3/9
# @description: 

from smtsdk.connection import Connection


class AliFreight(Connection):

    def __init__(self, shop):
        Connection.__init__(self)

        self.base_verbs = [
            "api.listFreightTemplate",
            "api.calculateFreight",
            "api.getFreightSettingByTemplateQuery"
        ]
        self.session = shop.session
        self.account = shop.account
        self.shop_id = shop.id

    def list_freight_template(self):
        params = {
            "access_token": self.account
        }
        self.need_signature = True
        response = self.execute("api.listFreightTemplate", params)
        return response

    def get_freight_setting_by_template_query(self, template_id):

        params = {
            "access_token": self.account,
            "templateId": template_id
        }
        self.need_signature = True
        response = self.execute("api.getFreightSettingByTemplateQuery", params)
        return response