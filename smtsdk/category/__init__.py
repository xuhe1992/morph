# -*- coding: utf-8 -*-

# @author: xuhe
# @date: 15/1/27
# @description:

import json
from smtsdk.connection import Connection


class AliCategory(Connection):

    def __init__(self, shop):
        Connection.__init__(self)

        self.base_verbs = [
            "getChildAttributesResultByPostCateIdAndPath",
            "api.recommendCategoryByKeyword",
            "api.getPostCategoryById",
            "api.getChildrenPostCategoryById",
            "api.getAttributesResultByCateId"
        ]
        self.session = shop.session
        self.account = shop.account
        self.shop_id = shop.id

    def get_children_categories(self, cate_id):
        params = {
            "cateId": cate_id,
            "access_token": self.account,
        }
        self.need_signature = True
        response = self.execute("api.getChildrenPostCategoryById", params)
        return response

    def get_category_attributes(self, cate_id, path=None):
        params = {
            "cateId": cate_id,
            "access_token": self.account,
        }
        if path:
            params["parentAttrValueList"] = json.dumps(path)
        self.need_signature = True
        response = self.execute("getChildAttributesResultByPostCateIdAndPath", params)
        return response

    def get_category_info(self, cate_id, path=None):
        params = {
            "cateId": cate_id,
            "access_token": self.account
        }
        if path:
            params.update(parentAttrValueList=json.dumps(path))
        self.need_signature = True
        response = self.execute("api.getPostCategoryById", params)
        return response

    def get_recommend_list(self, keyword):
        params = {
            "keyword": keyword,
            "access_token": self.account
        }
        self.need_signature = True
        response = self.execute("api.recommendCategoryByKeyword", params)
        return response


# if __name__ == "__main__":
#     from morph.lib.model.shop import Shop
#     shop = Shop()
#     shop.account = "3dc01f63-48b5-4292-9ca0-350f1c61d0be"
#     shop.session = "fdfea271-050b-4876-a522-126dd6163e06"
#     ac = AliCategory(shop)
#     print ac.get_category_attributes(200000392, [[281, 1887]])

