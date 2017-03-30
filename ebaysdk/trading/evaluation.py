# -*- coding=utf-8 -*-

"""
@author: xuhe
@date:
@version:
@description:
"""

from furion.config import settings
from ebaysdk.trading import Connection as Trading


class EbayEvaluation(Trading):

    """
    eBay评价反馈SDK，是对ebaysdk.trading.Connection的继承，用于实现相应的FeedBack业务逻辑
    eBay评价反馈调用简介：http://developer.ebay.com/DevZone/guides/ebayfeatures/Development/Sales-Feedback.html
    OrderLineItemID = ItemID + TransactionID，当刊登方式是拍卖的时候，TransactionID为0.
    可以理解为：商品拍卖时商品只有一件，只需通过ItemID即可区分并查找到订单中的某个条目，而其他刊登方式产品库存为多件，TransactionID各不相同
    """

    def __init__(self, site_id, token, production=True):
        self.token = token
        self.site_id = site_id
        self.domain = "api.ebay.com" if production else "api.sandbox.ebay.com"
        Trading.__init__(
            self,
            domain=self.domain,
            config_file=settings.ebay_yaml,
            siteid=self.site_id,
            token=self.token
        )

    def get_feedback(self, comment_type=None, feedback_id=None, feedback_type=None, user_id=None,
                     transaction_id=None, order_line_item_id=None, current_page=None, page_size=None):
        """
        根据筛选条件获取评价反馈列表
        :param comment_type:        评价类型，好评、中评、差评
        :param feedback_id:         FeedBackID
        :param feedback_type:       FeedBack类型
                                        FeedbackLeft获取自己所有曾经留下的评价
                                        FeedbackReceived获取自己所有收到的评价
                                        FeedbackReceivedAsBuyer获取自己作为卖家收到的评价
                                        FeedbackReceivedAsSeller获取自己作为买鸡收到的评价
        :param user_id:             UserID
        :param transaction_id:      1个订单包含1到多个TransactionID
        :param order_line_item_id:  OrderLineItemID = ItemID + TransactionID
        :param current_page:        当前页
        :param page_size:           每页数量
        :return:
        """
        req = {
            "WarningLevel": "High",
        }
        if comment_type:
            req["CommentType"] = comment_type
        if feedback_id:
            req["FeedbackID"] = feedback_id
        if feedback_type:
            req["FeedbackType"] = feedback_type
        if user_id:
            req["UserID"] = user_id
        if transaction_id:
            req["TransactionID"] = transaction_id
        if order_line_item_id:
            req["OrderLineItemID"] = order_line_item_id
        if current_page and page_size:
            req["Pagination"] = {
                "EntriesPerPage": page_size,
                "PageNumber": current_page
            }
        response = self.execute("GetFeedback", req)
        print response.dict()
        return response.dict()

    def get_awaiting_feedback(self, current_page, page_size, sort_type=None):
        """
        获取等待被评价的OrderLineItems，OrderLineItemID = ItemID + TransactionID
        :param current_page: 当前页
        :param page_size:    每页数量
        :param sort_type:    排序方式
                             EndTime EndTimeDescending FeedbackLeft FeedbackLeftDescending
                             FeedbackReceived FeedbackReceivedDescending Title TitleDescending
                             UserID UserIDDescending
        :return:
        """
        req = {
            "Pagination": {
                "EntriesPerPage": page_size,
                "PageNumber": current_page
            },
            "WarningLevel": "High",
        }
        if sort_type:
            req["Sort"] = sort_type
        response = self.execute("GetItemsAwaitingFeedback", req)
        print response.dict()
        return response.dict()

    def leave_feedback(self, comment_text, target_user, comment_type="Positive",
                       item_id=None, order_line_item_id=None, transaction_id=None):
        """
        改API可以买家使用也可以卖家使用，卖家使用时，查看了eBay后台发现卖家一般发送Positive Feedback，
        而且只需要写一个CommentText即可。
        :param comment_text:       评价内容，推荐值有以下：
                                   1.Great communication. A pleasure to do business with.
                                   2.Good buyer, prompt payment, valued customer, highly recommended.
                                   3.Thank you for an easy, pleasant transaction. Excellent buyer. A++++++.
                                   4.Quick response and fast payment. Perfect! THANKS!!
                                   5.Hope to deal with you again. Thank you.
        :param comment_type:       评价类型，Negative/Neutral/Positive
        :param target_user:        目标用户
        :param item_id:            Item ID
        :param order_line_item_id: OrderLineItemID = ItemID + TransactionID
        :param transaction_id:     1个订单包含1到多个TransactionID
        :return:
        """
        req = {
            "CommentText": comment_text,
            "CommentType": comment_type,
            "TargetUser": target_user,
            "WarningLevel": "High",
        }
        if item_id:
            req["ItemID"] = item_id
        if order_line_item_id:
            req["OrderLineItemID"] = order_line_item_id
        if transaction_id:
            req["TransactionID"] = transaction_id
        response = self.execute("LeaveFeedback", req)
        print response.dict()
        return response.dict()

    def response_to_feedback(self):
        pass