# -*- coding=utf-8 -*-

"""
@author: xuhe
@date: 2016/10/20
@version:
@description:
"""

from smtsdk.connection import Connection
from morph.lib.model.shop import Shop


class AliEvaluation(Connection):

    """
    速卖通评价SDK，主要的接口为获取评价列表以及卖家对订单进行评价
    """

    def __init__(self, shop):
        Connection.__init__(self)
        self.base_verbs = [
            "api.evaluation.querySellerEvaluationOrderList",
            "api.evaluation.saveSellerFeedback"
        ]
        self.session = shop.session
        self.account = shop.account
        self.shop_id = shop.id
        self.need_signature = True

    def get_evaluation_list(self, current_page=None, page_size=None, order_ids=None):
        """
        查询待卖家评价的订单
        :param current_page: 当前页，可选
        :param page_size:    每页显示数量，可选
        :param order_ids:    订单ID列表，以逗号分隔开
        :return: 返回订单ID的列表
        """
        params = {
            "access_token": self.account
        }
        if order_ids:
            params["orderIds"] = order_ids
        if current_page and page_size:
            params["currentPage"] = current_page
            params["pageSize"] = page_size
        response = self.execute('api.evaluation.querySellerEvaluationOrderList', params)
        return response

    def reply_evaluation(self, order_id, score, content):
        """
        对订单进行回复
        :param order_id: 订单ID
        :param score:    评分，1-5分
        :param content:  评价内容
        :return:
        """
        params = {
            "access_token": self.account,
            "orderId": order_id,
            "score": score,
            "feedbackContent": content
        }
        response = self.execute('api.evaluation.saveSellerFeedback', params)
        return response

if __name__ == "__main__":
    shop = Shop()
    shop.account = "a36c6039-cca4-4638-a84a-dc1ec9c4200f"
    shop.session = "0bdf6f64-372d-4b6a-b68b-5efe64bc18bd"
    shop.site_id = 2
    shop.platform = "AliExpress"
    shop.name = 'Limerence'
    handler = AliEvaluation(shop)
    # result = handler.get_msg_detail_list(
    #     channel_id="66947353601", msg_source="message_center"
    # )
    #
    # result = handler.get_msg_relation_list(
    #     msg_source="message_center"
    # )

    # result = handler.get_evaluation_list(current_page=1, page_size=3)
    # import json
    # print json.dumps(result, indent=2)