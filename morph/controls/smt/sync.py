# -*- coding: utf-8 -*-

"""
@author: xuhe
@date: 17/3/31
@description: 
"""

from morph.lib.model.attachment import Attachment
from morph.lib.model.channel import Channel
from morph.lib.model.message import Message
from morph.lib.model.session import sessionCM
from morph.task.sync_customer_detail import sync_smt_customer_detail
from smtsdk.message import AliMessage
from smtsdk.evaluation import AliEvaluation


class SyncSmtCustomer(object):

    def __init__(self, shop, timestamp=None):
        self.shop = shop
        self.timestamp = timestamp
        self.msg_handler = AliMessage(shop)
        self.elt_handler = AliEvaluation(shop)

    def sync_message_list(self, msg_source, current_page=1, page_size=100):
        """
        同步订单留言
        :return:
        """
        with sessionCM() as session:
            while True:
                result = self.msg_handler.get_msg_relation_list(msg_source, current_page, page_size)
                if not result["success"]:
                    return result["exception"]
                for relation in result:
                    # 判断当前同步下来的Channel是否存在
                    chanel = Channel.find_by_origin_id(session, relation["channelId"])
                    # 若和上次lastMessageId相同，就不用再获取详情
                    if chanel and relation["lastMessageId"] == chanel["last_msg_id"]:
                        continue
                    Channel.update(
                        session, chanel, seller_id=relation["childId"], seller_name=relation["childName"],
                        buyer_id=relation["otherLoginId"], buyer_name=relation["otherName"],
                        read_stat=relation["readStat"], deal_stat=relation["dealStat"], open_date="",
                        close_date="", closed_by="", flag=relation["rank"], origin_id=relation["channelId"],
                        msg_source=msg_source, relation_type="", relation_id="", last_msg_date=relation["messageTime"],
                        last_msg_id=relation["lastMessageId"], last_msg_content=relation["lastMessageContent"]
                    )
                    sync_smt_customer_detail.delay(self, chanel.id, msg_source)
                if len(result) == 0:
                    break

    def sync_message_detail(self, channel_id, msg_source, current_page=1, page_size=100):
        """
        同步订单留言
        :return:
        """
        with sessionCM() as session:
            channel = Channel.find_by_id(session, channel_id)
            additional_flag = False
            while True:
                result = self.msg_handler.get_msg_detail_list(channel_id, msg_source, current_page, page_size)
                if not result["success"]:
                    return result["exception"]
                for message in result:
                    old_msg = Message.find_by_origin_id(session, message["id"])
                    if old_msg:
                        continue
                    Message.create(
                        session, channel_id=channel_id, origin_id=message["id"], content=message["content"],
                        image_urls=";".join([im["sPath"] for im in message["filePath"]]),
                        receive_time=message["gmtCreate"],
                    )
                    if additional_flag:
                        continue
                    if not channel.relation_type or not channel.relation_id:
                        Channel.update(
                            session, channel, shop_id=self.shop.id,
                            relation_type=message["messageType"],
                            relation_id=message["typeId"]
                        )
                        Attachment.create(
                            session, channel_id=channel_id, name=message["productName"],
                            image_url=message["productImageUrl"], product_url=message["productDetailUrl"],
                            order_url=message["orderUrl"]
                        )
                        additional_flag = True
                if len(result) == 0:
                    break

    def sync_evaluation(self, page_no, page_size):
        """
        同步评价信息
        :param page_no:
        :param page_size:
        :return:
        """
        pass

    def execute(self):
        pass