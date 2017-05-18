# -*- coding=utf-8 -*-

"""
@author:xuhe
@date: 2017-03-20
@version:
@description:
"""

from smtsdk.connection import Connection


class AliCustomer(Connection):

    """
    速卖通消息SDK，以下是在使用SDK过程中使用的术语，用于参考。
    channel_id: 卖家与某一买家建立通信关系的通道ID
    msg_source: 用于标识站内信还是订单留言，message_center代表站内信，order_msg代表订单留言
    rank:       标签，rank0-rank5分别代表白，红，橙，绿，蓝，紫6种颜色
    """

    def __init__(self, shop):
        Connection.__init__(self)

        self.base_verbs = [
            "api.queryMsgDetailList", "api.queryMsgRelationList",
            "api.updateMsgProcessed", "api.updateMsgRead",
            "api.updateMsgRank", "api.queryMsgDetailListByBuyerId",
            "api.addMsg"
        ]
        self.session = shop.session
        self.account = shop.account
        self.shop_id = shop.id
        self.need_signature = True

    def get_msg_detail_list(self, channel_id, msg_source, current_page=1, page_size=100):
        """
        获取指定站内信/订单留言的聊天记录，以列表形式返回，最多返回5000条数据。
        :param channel_id:   通道ID
        :param msg_source:   查询类型
        :param current_page: 当前页
        :param page_size:    每页显示数量0-100
        :return: 返回消息列表
        """
        params = {
            "access_token": self.account,
            "currentPage": current_page,
            "pageSize": page_size,
            "msgSources": msg_source,
            "channelId": channel_id
        }
        response = self.execute('api.queryMsgDetailList', params)
        return response

    def get_msg_relation_list(self, msg_source, current_page=1, page_size=100, filter_condition=None):
        """
        获取与当前卖家建立通信关系的所有通道ID，最多返回5000条数据。
        :param msg_source:       查询类型
        :param filter_condition: 筛选条件，rank0-rank5，以及readStat:未读和dealStat:未处理
        :param current_page:     当前页
        :param page_size:        每页显示数量0-100
        :return: 返回关系列表
        """
        params = {
            "access_token": self.account,
            "currentPage": current_page,
            "pageSize": page_size,
            "msgSources": msg_source,
        }
        if filter_condition:
            params["filter"] = filter_condition
        response = self.execute('api.queryMsgRelationList', params)
        return response

    def update_msg_process_status(self, channel_id, deal_status):
        """
        更新指定通道ID的处理状态为未处理或已处理
        :param channel_id:  通道ID
        :param deal_status: 处理状态，0:未处理，1:已处理
        :return:
        """
        params = {
            "access_token": self.account,
            "channelId": channel_id,
            "dealStat": deal_status
        }
        response = self.execute('api.updateMsgProcessed', params)
        return response

    def update_msg_read_status(self, channel_id, msg_source):
        """
        更新指定通道ID的处理状态为已读
        :param channel_id:  通道ID
        :param msg_source:  查询类型
        :return:
        """
        params = {
            "access_token": self.account,
            "channelId": channel_id, "msgSources": msg_source
        }
        response = self.execute('api.updateMsgRead', params)
        return response

    def update_msg_rank(self, channel_id, rank):
        """
        为指定通道ID打标签
        :param channel_id:  通道ID
        :param rank:        rank0-rank5
        :return:
        """
        params = {
            "access_token": self.account,
            "channelId": channel_id,
            "rank": rank
        }
        response = self.execute('api.updateMsgRank', params)
        return response

    def get_msg_by_buyer(self, buyer_id, seller_id, current_page=1, page_size=100):
        """
        根据买卖家ID查询所有站内信信息，最多返回5000条数据。
        :param buyer_id:     买家ID
        :param seller_id:    卖家ID
        :param current_page: 当前页
        :param page_size:    每页显示数量0-100
        :return: 返回站内信列表
        """
        params = {
            "access_token": self.account,
            "currentPage": current_page,
            "pageSize": page_size,
            "buyerId": buyer_id,
            "sellerId": seller_id
        }
        response = self.execute('api.queryMsgDetailListByBuyerId', params)
        return response

    def add_msg(self, channel_id, buyer_id, content, msg_sources, image=None):
        """
        在指定通道ID上发布新的消息，用于回复订单留言或站内信
        :param channel_id:  通道ID
        :param buyer_id:    卖家ID
        :param content:     消息内容
        :param msg_sources: 查询类型
        :param image:       图片地址链接
        :return:
        """
        params = {
            "access_token": self.account,
            "channelId": channel_id,
            "msgSources": msg_sources,
            "buyerId": buyer_id,
            "content": content
        }
        if image:
            params["imgPath"] = image
        response = self.execute('api.addMsg', params)
        return response
