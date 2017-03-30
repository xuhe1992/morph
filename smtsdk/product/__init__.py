# -*- coding: utf-8 -*-

# @author: xuhe
# @date: 15/1/26
# @description:

import json
from smtsdk.connection import Connection


class AliProduct(Connection):

    def __init__(self, shop):
        Connection.__init__(self)
        self.base_verbs = [
            "api.findAeProductStatusById", "api.findAeProductProhibitedWords",
            "api.editSKUStocks", "api.getSizeChartInfoByCategoryId",
            "api.setSizeChart", "api.sizeModelsRequiredForPostCat",
            "api.editAeProduct", "api.findAeProductById", "api.createProductGroup",
            "api.postAeProduct", "api.findProductInfoListQuery",
            "sizeModelIsRequiredForPostCart", "api.getWindowProduct",
            "api.editProductCategoryAttributes", "api.setGroup",
            "api.queryProductGroupIdByProductId", "api.getProductGroupList",
            "api.editProductCidAttIdSku", "api.editSimpleProductFiled",
            "api.getAttributeMissingProductList", "api.laimTaobaoProducts4API",
            "api.offShowindowProduct", "api.setShopwindowProduct",
            "api.queryPromiseTemplateById", "api.listTbProductByIds",
            "api.findAeProductDetailModuleListByQuery", "api.findAeProductModuleById",
            "api.onlineAeProduct", "alibaba.product.postMultilanguageAeProduct",
            "api.offlineAeProduct", "api.editSingleSkuPrice", "api.editSingleSkuStock",
            "api.claimTaobaoProducts4API", "api.findAeProductDetailModuleListByQurey",
            "api.editMultilanguageProduct"
        ]
        self.session = shop.session
        self.account = shop.account
        self.shop_id = shop.id

    def find_product_by_id(self, product_id):
        params = {
            "access_token": self.account,
            "productId": product_id
        }
        self.need_signature = True
        response = self.execute("api.findAeProductById", params)
        return response

    def get_product_groups(self):
        params = {
            "access_token": self.account
        }
        self.need_signature = True
        response = self.execute("api.getProductGroupList", params)
        return response

    def create_product_group(self, name, parent_id):
        params = {
            "access_token": self.account,
            "name": name,
            "parentId": parent_id
        }
        self.need_signature = True
        response = self.execute("api.createProductGroup", params)
        return response

    def find_product_list(self, product_status_type, page=1):
        if product_status_type not in [
            "onSelling", "offline", "auditing", "editingRequired"
        ]:
            return None
        params = {
            "access_token": self.account,
            "productStatusType": product_status_type,
            "currentPage": page,
            "pageSize": 80
        }
        self.need_signature = True
        response = self.execute("api.findProductInfoListQuery", params)
        return response

    def find_product_list_by_terms(self, subject, group_id, offline_time, pro_id, page=1):
        params = {
            "access_token": self.account,
            "productStatusType": "onSelling",
            "subject": subject,
            "groupId": group_id,
            "offLineTime": offline_time,
            "productId": pro_id,
            "currentPage": page,
            "pageSize": 80
        }
        self.need_signature = True
        response = self.execute("api.findProductInfoListQuery", params)
        return response

    def upload_product(self, product):
        product.update(access_token=self.account)
        for key, value in product.iteritems():
            if type(value) in [list, dict]:
                product[key] = json.dumps(value)
        params = product
        self.need_signature = True
        response = self.execute("api.postAeProduct", params)
        return response

    def update_product(self, item_id, product):
        product.update({
            "access_token": self.account,
            "productId": item_id
        })
        for key, value in product.iteritems():
            if type(value) in [list, dict]:
                product[key] = json.dumps(value)
        params = product
        self.need_signature = True
        response = self.execute("api.editAeProduct", params)
        return response

    def edit_simple_product_filed(self, product_id, name, value):
        params = {
            "access_token": self.account,
            "productId": product_id,
            "fiedName": name,
            "fiedvalue": str(value)
        }
        self.need_signature = True
        response = self.execute("api.editSimpleProductFiled", params)
        return response

    def edit_product_cid_att_id_sku(self, product_id, product_skus):
        params = {
            "access_token": self.account,
            "productId": product_id,
            "productSkus": json.dumps(product_skus)
        }
        self.need_signature = True
        response = self.execute("api.editProductCidAttIdSku", params)
        return response

    def query_promise_template_by_id(self, template_id=-1):
        params = {
            "access_token": self.account,
            "templateId": template_id
        }
        self.need_signature = True
        response = self.execute("api.queryPromiseTemplateById", params)
        return response

    def offline_products(self, product_ids):
        params = {
            "access_token": self.account,
            "productIds": product_ids
        }
        self.need_signature = True
        response = self.execute("api.offlineAeProduct", params)
        return response

    def online_products(self, product_ids):
        params = {
            "access_token": self.account,
            "productIds": product_ids
        }
        self.need_signature = True
        response = self.execute("api.onlineAeProduct", params)
        return response

    def edit_single_sku_price(self, product_id, sku_id, price):
        params = {
            "access_token": self.account,
            "productId": product_id,
            "skuId": sku_id,
            "skuPrice": price
        }
        self.need_signature = True
        response = self.execute("api.editSingleSkuPrice", params)
        return response

    def edit_single_sku_stock(self, product_id, sku_id, stock):
        params = {
            "access_token": self.account,
            "productId": product_id,
            "skuId": sku_id,
            "ipmSkuStock": stock
        }
        self.need_signature = True
        response = self.execute("api.editSingleSkuStock", params)
        return response

    def edit_single_prop(self, product_id, prop):
        params = {
            "access_token": self.account,
            "productId": product_id,
        }
        params.update(prop)
        self.need_signature = True
        response = self.execute("api.editAeProduct", params)
        return response

    def edit_product_props(self, product_id, props):
        params = {
            "access_token": self.account,
            "productId": product_id,
        }
        if isinstance(props, list):
            params["productCategoryAttributes"] = json.dumps(props)
        else:
            params["productCategoryAttributes"] = props
        self.need_signature = True
        response = self.execute("api.editProductCategoryAttributes", params)
        return response

    def claim_product_to_smt(self, url):
        params = {
            "access_token": self.account,
            "url": url
        }
        self.need_signature = True
        response = self.execute("api.claimTaobaoProducts4API", params)
        return response

    def query_info_template(self, index=1):
        params = {
            "access_token": self.account,
            "moduleStatus": "approved",
            "pageIndex": index
        }
        self.need_signature = True
        response = self.execute("api.findAeProductDetailModuleListByQurey", params)
        return response

    def get_size_chart(self, category_id):
        params = {
            "access_token": self.account,
            "categoryId": category_id
        }
        self.need_signature = True
        response = self.execute("api.getSizeChartInfoByCategoryId", params)
        return response

    def get_size_model(self, post_id):
        params = {
            "access_token": self.account,
            "postCatId": post_id
        }
        self.need_signature = True
        response = self.execute("api.sizeModelsRequiredForPostCat", params)
        return response

    def find_prohibited_words(self, category_id, title=None, description=None, specifics=None):
        params = {
            "access_token": self.account,
            "categoryId": category_id,
        }
        if title:
            params["title"] = title
        if description:
            params["detail"] = description
        if specifics:
            params["productProperties"] = json.dumps(specifics)
        self.need_signature = True
        response = self.execute("api.findAeProductProhibitedWords", params)
        return response

    def upload_multi_lang_product(self, product):
        product.update(access_token=self.account)
        for key, value in product.iteritems():
            if type(value) in [list, dict]:
                product[key] = json.dumps(value)
        params = product
        self.need_signature = True
        response = self.execute("alibaba.product.postMultilanguageAeProduct", params)
        return response

    def edit_multi_lang_product(self, product_id, language, title, description, mobile_detail):
        params = {
            "access_token": self.account,
            "productId": product_id,
            "locale": language
        }
        flag = False
        if title:
            params["subject"] = title
            flag = True
        if description:
            params["detail"] = description
            flag = True
        if mobile_detail:
            if type(mobile_detail) in [list, dict]:
                params["mobileDetail"] = json.dumps(mobile_detail)
            else:
                params["mobileDetail"] = mobile_detail
            flag = True
        if flag:
            self.need_signature = True
            response = self.execute("api.editMultilanguageProduct", params)
            return response


# if __name__ == "__main__":
#     from furion.lib.model.shop import Shop
#     shop = Shop()
#     shop.session = "2190b383-d048-47f1-a14f-5323981557cb"
#     shop.account = "304d4920-3e1e-47c5-9dd1-39c5753e02af"
#     ap = AliProduct(shop)
#     print ap.find_product_by_id("32714832536")
