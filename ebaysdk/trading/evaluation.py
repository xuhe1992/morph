# -*- coding=utf-8 -*-

"""
@author: xuhe
@date:
@version:
@description:
"""

from morph.config import settings
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

    def get_feedback(self, comment_type=None, feedback_id=None, feedback_type=None, user_id=None, item_id=None,
                     transaction_id=None, order_line_item_id=None, current_page=None, page_size=None):
        """
        根据筛选条件获取评价反馈列表
        :param comment_type:        评价类型，好评、中评、差评
        :param feedback_id:         FeedBackID
        :param feedback_type:       FeedBack类型
                                        FeedbackLeft获取自己所有曾经留下的评价
                                        FeedbackReceived获取自己所有收到的评价
                                        FeedbackReceivedAsBuyer获取自己作为卖家收到的评价
                                        FeedbackReceivedAsSeller获取自己作为买家收到的评价
        :param user_id:             UserID
        :param item_id:             item_id 返回这个item的最多100个评价，
        :param transaction_id:      1个订单包含1到多个TransactionID，单个订单项（eBay 中的 order line item）
        :param order_line_item_id:  OrderLineItemID = ItemID + TransactionID
        :param current_page:        当前页
        :param page_size:           每页数量
        :return:
        """
        req = {
            "WarningLevel": "High",
            "DetailLevel": "ReturnAll"
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
            "DetailLevel": "ReturnAll"
        }
        if sort_type:
            req["Sort"] = sort_type
        response = self.execute("GetItemsAwaitingFeedback", req)
        return response.dict()

    def leave_feedback(self, comment_text, target_user, comment_type="Positive",
                       item_id=None, order_line_item_id=None, transaction_id=None):
        """
        该API可以买家使用也可以卖家使用，卖家使用时，查看了eBay后台发现卖家一般发送Positive Feedback，
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
        return response.dict()

    def response_to_feedback(self):
        pass


nm = "AgAAAA**AQAAAA**aAAAAA**7HTjVw**nY+sHZ2PrBmdj6wVnY+sEZ2PrA2dj6ABkoGoD5aHpAqdj6x9nY+seQ**94UCAA**AAMAAA**UGJaMLGzkw/V30Q7yrFVpkDxh9+F1v7X7taOlLW6WeEQCY/F6PhqPrjJfFLfw5rg93LNBvSQV4hO/cLtHS1K059mXzg61q4xHToNFk2uK+DdoFlCGbc1BD0TRyZ9zOSw4peeHJy/XUG2GwzkyPSrkBlU8X8e2IcZiyqCEILF0yl0ffDJy4Yz62JZVYCCX7HzvI/39N3ROGcUpCVbmxPE+QJI4a2Xst9ApBikHreVDntERITCRj8FhnnmAoDHGWziGN5GlNOQ40ETGX9GUX9yjK31haSpTpIsJRQBYhYeOYwo+F+LV5mFR55XDtuKD837jmKGZvpwll2pN4XhJfVbU7VFWbqyi2p4ccjxNEKXqmbJSSESvXmhiNK5J5EmAZVxh0BmXnNAHYCMJ1gZ7+sa4shnnzH12wcjMjK679iwXyYiK1YTrNmLNei4UeDFBfb2fzqm+eSDQIBK9g+HX/fZkTssU0O1m59wTeS+9GG6Bu7wTZyjU5cbCbjlQl6J4xhy4rs+efJLLAx/PfXmAODHgPF1Ai4rF/YYogFy+V9G0SiQJLQz31yxD3uJuDNyVoEB7/voPAvVutUvZcJzw2LAHIETfHG7GNMoHFA1fyLOF76YIZzsxBylxRY/x12gLlHFaKrtNAJRWpbKHO6usD0GMehDd9a/ALlSqHMPolKyaN6RMWEdov/Drq5PYTW+2OmO8GYyzrmCSk8s+OEv4LhLwkL4YBdYZyKoGo7Qf2FTqbfuYOKMblMi2MDACFSYKuvZ"
nm = 'AgAAAA**AQAAAA**aAAAAA**C6d8Vw**nY+sHZ2PrBmdj6wVnY+sEZ2PrA2dj6AAkIGgC5GKqAudj6x9nY+seQ**94UCAA**AAMAAA**eCsndGWz9QGRmaERU4mzDBDmCBIgLA2Yk1PaZLnrOjPvIMXNITpIeH9PRAqAPdykJ9AihKAFLRKl4AfIS6c2sNf9AomUiUXlmm5j+OpTS+/C9c/gIpAQrBY2AELmkq8QIpWQ5bmgvFDr7jn3BxpwwcUDCeAv/pUcvQYpXnyDxI8H0bIsKQudUKaL7sS/5gVqgtzN561rt3s5lBSpfoP4qzdQ9iSfaIWIX7z40XE18BRLDsY/3rrsGlASwaShSul7StJWkjd0NL3AiYPiPuJtRzahUTtPRLP5NxxKJNJZhEHXRqXNcFVN3FYEAuiKDb0hE2Jr9KXL3A4lJNjaNhNquGkqTyA9NB3Vei2zCZgVWvlaQAavJhn+ZFBdQBFjNBdahK78s+Ve+Ym7bbEXKlhQYUFmBcXIUgOTr3MR2ghe3peHlRSSbKeaPDTIKcJ5f6PNKqGjHaQYOnu8igGluHVxb2gKiXkT/UXH08lFzOcC3bP7WkEoo/DLPBbxFsguCbuY0gtjyeVUcDU3idpFbjrCpy2bBlPBp9Qts3Fdw87O1guOk+B6UU/LEuGYbcRRyzWQie1QWbgiFSPbA4rLYemIrsh6iIRgKxASFI+ZIeqVdYsALy8PHsEE6jNzQMcf5R2e/DBhW7Rf/20by6yZ3eb6ONBlm9UWVqsxMRL0aYfKi1PIG1V1RKaq+ul5ypiTDPK6lLadihibYn2I8BvD4n+VdRVNcDCYpBppjKrNtR+UgI+1Jr+n2tAc5B9xOq/0NCnr'
si = "0"


def tor(response):
    import json
    print json.dumps(response, indent=2, encoding="utf-8")

# handler = EbayEvaluation(si, nm)

# rb = handler.get_awaiting_feedback(1, 200, sort_type='EndTime')
# tor(rb["ItemsAwaitingFeedback"]["TransactionArray"]["Transaction"])
# tor(rb["ItemsAwaitingFeedback"]["TransactionArray"]["Transaction"])
# print result.keys()
# print result["ItemsAwaitingFeedback"].keys()
# print result["ItemsAwaitingFeedback"]["TransactionArray"].keys()
# print result["ItemsAwaitingFeedback"]["TransactionArray"]["Transaction"]
# tor(result["ItemsAwaitingFeedback"]["TransactionArray"]["Transaction"])


# n1 = 0
# n2 = 0
# n3 = 0
# for item in rb["ItemsAwaitingFeedback"]["TransactionArray"]["Transaction"]:
#     # if item.get("FeedbackReceived " ""):
#     #     tor(item)
#     #     # n2 += 1
#     result = handler.get_feedback(order_line_item_id=item["OrderLineItemID"])
#     print item.get("OrderLineItemID", "qwer")
#     if not result.get("FeedbackDetailArray", ""):
#         # tor(result)
#         n2 += 1
#         continue
#     detail = result["FeedbackDetailArray"]["FeedbackDetail"]
#     if detail["Role"] != "Buyer":
#         tor(detail)
#         n1 += 1
#     else:
#         n3 += 1
# print len(rb["ItemsAwaitingFeedback"]["TransactionArray"]["Transaction"])
# print "买家回复：" + str(n1)
# print "买家未回复: " + str(n2)
# print "卖家回复: " + str(n3)

# for item in result["ItemsAwaitingFeedback"]["TransactionArray"]["Transaction"]:
#     r2 = handler.get_feedback(order_line_item_id=item["OrderLineItemID"])
#     # tor(r2)
#     feedback_detail = r2.get("FeedbackDetailArray", "")
#     if feedback_detail:
#         feedback_detail = feedback_detail["FeedbackDetail"]
#         tor(feedback_detail)
#         if feedback_detail["CommentingUser"] != "yaya-wholesale365":
#             print "qwer" + feedback_detail["CommentText"]
# for
# tor(handler.get_feedback())


# count = 0
# while True:
#     count +=1
#     result = handler.get_feedback(current_page=count, page_size=100) # feedback_id=1065290730025 ,comment_type=[ 'Positive'], current_page=count, page_size=100)
#     # tor(result)
#     print result.keys()
#     detail_array = result["FeedbackDetailArray"]
#     print detail_array.keys()
#     tor(result["PaginationResult"])
#     tor(result["FeedbackSummary"])
#
#     detail = detail_array["FeedbackDetail"]
#     if isinstance(detail, dict):
#         detail = [detail]
#     # tor(result)
#     # tor(detail)
#     # for item in detail:
#     #     # if item["Role"] != "Seller":
#     #     print item["CommentingUser"], item["CommentingUserScore"], item["Role"], item["OrderLineItemID"], item.get("CommentText")
#     #     print ""
#     print len(detail)
#     if len(detail) < 100:
#         break

# result = handler.get_feedback(item_id='263059133157', order_line_item_id='263059133157-2041340001016')
# d = result["FeedbackDetailArray"]["FeedbackDetail"]
# tor(d)

