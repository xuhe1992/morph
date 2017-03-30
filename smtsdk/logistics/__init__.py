# -*- coding: utf-8 -*-

# @author: xuhe
# @date: 15/9/9
# @description:
import traceback
import ujson as json
from furion.lib.model.shop import Shop
from furion.lib.utils.logger_util import logger

from smtsdk.connection import Connection


class AliLogistics(Connection):

    def __init__(self, shop):
        Connection.__init__(self)
        self.base_verbs = [
            "api.listLogisticsService", "api.getPrintInfos", "api.sellerModifiedShipment",
            "api.getOnlineLogisticsInfo", "api.getPrintInfo", "api.getOnlineLogisticsServiceListByOrderId",
            "api.createWarehouseOrder", "api.qureyWlbDomesticLogisticsCompany", "api.sellerShipment",
            "api.queryTrackingResult", "api.getAllProvince", "api.getNextLevelAddressData",
            "alibaba.ae.api.getLogisticsSellerAddresses"
        ]
        self.session = shop.session
        self.account = shop.account
        self.shop_id = shop.id

    def list_supported_service(self):
        params = {
            "access_token": self.account,
        }
        self.need_signature = True
        response = self.execute("api.listLogisticsService", params)
        return response

    def qurey_wbl_domestic_logistics_company(self):
        params = {
            "access_token": self.account,
        }
        self.need_signature = True
        response = self.execute("api.qureyWlbDomesticLogisticsCompany", params)
        return response

    def list_domestic_company(self):
        params = {
            "access_token": self.account
        }
        self.need_signature = True
        response = self.execute("api.qureyWlbDomesticLogisticsCompany", params)
        return response

    def get_print_info(self, logistics_num, track_no):
        params = {
            "access_token": self.account,
            "id": int(logistics_num),
            "internationalLogisticsId": track_no,
        }
        self.need_signature = True
        response = self.execute("api.getPrintInfo", params)
        return response

    def get_print_infos(self, nums):
        params = {
            "access_token": self.account,
            "printDetail": True,
            "warehouseOrderQueryDTOs": json.dumps([{"internationalLogisticsId": num} for num in nums])
        }
        self.need_signature = True
        response = self.execute("api.getPrintInfos", params)
        return response

    def get_online_logistics_service_list_by_order_id(self, order_id):
        params = {
            "access_token": self.account,
            "orderId": order_id,
        }
        response = self.execute("api.getOnlineLogisticsServiceListByOrderId", params)
        return response

    def get_all_province(self):
        params = {
            "access_token": self.account,
        }
        response = self.execute("api.getAllProvince", params)
        return response

    def get_next_level_address_data(self, parent_code):
        params = {
            "access_token": self.account,
            "areaId": parent_code
        }
        response = self.execute("api.getNextLevelAddressData", params)
        return response

    def create_warehouse_order(self, order_no, logistics_type, domestics_type, domestics_name,
                               domestics_num, products_info, address_info, refund, note=""):
        params = {
            "access_token": self.account,
            "tradeOrderId": order_no,
            "tradeOrderFrom": "ESCROW",
            "warehouseCarrierService": logistics_type,
            "domesticLogisticsCompanyId": domestics_type or "-1",
            "domesticLogisticsCompany": domestics_name or "-1",
            "domesticTrackingNo": domestics_num or "None",
            "declareProductDTOs": products_info,
            "addressDTOs": json.dumps(address_info),
            "remark": note,
            "undeliverableDecision": refund
        }
        self.need_signature = True
        for key, value in params.iteritems():
            if type(value) in [list, dict]:
                params[key] = json.dumps(value)
        response = self.execute("api.createWarehouseOrder", params)
        return response

    def get_by_id(self, order_id):
        params = {
            "access_token": self.account,
            "orderId": order_id,
        }
        self.need_signature = True
        response = self.execute("api.getOnlineLogisticsInfo", params)
        return response

    def seller_shipment(self, order_no, logistics_no, service_name =""):
        params = {
            "access_token": self.account,
            "serviceName": service_name,
            "logisticsNo": logistics_no,
            "sendType": "all",
            "outRef": order_no,
        }
        self.need_signature = True
        response = self.execute("api.sellerShipment", params)
        return response

    def get_seller_address(self):
        params = {
            "access_token": self.account,
            "request": json.dumps(["sender", "pickup", "refund"])
        }
        self.need_signature = True
        response = self.execute("alibaba.ae.api.getLogisticsSellerAddresses", params)
        return response

if __name__ == "__main__":
    shop = Shop()
    shop.session = "0aaf0faf-590a-4d49-bcef-21171766745e"
    shop.account = "48d74966-d355-4296-87bb-ad5117c0512c"
    AT = AliLogistics(shop)
    print AT.get_by_id("500997895186903")
    # res1 = AT.get_print_info(3374557145, "RF449915291CN")
    # print res1
    # nums = ["04245701278", "04245844360", "04245701264"]
    # print AT.get_print_infos(nums)
    # print AT.list_supported_service()