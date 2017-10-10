# -*- coding: utf-8 -*-

"""
@author: xuhe
@date: 17/3/31
@description: 
"""
import time
import json
from morph.lib.utils.logger_util import logger
from morph.lib.model.session import sessionCM
from morph.lib.model.attachment import Attachment
from morph.lib.model.channel import Channel
from morph.lib.model.message import Message
from morph.lib.model.evaluation import Evaluation
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
                print type(result), len(result)
                print result
                if not result["success"]:
                    return  # result["exception"]
                current_page += 1
                for relation in result.get("result", []):
                    print relation
                    # 判断当前同步下来的Channel是否存在
                    chanel = Channel.find_by_origin_id(session, relation["channelId"])
                    # 若和上次lastMessageId相同，就不用再获取详情
                    if chanel and relation["lastMessageId"] == chanel["last_msg_id"]:
                        continue
                    if len(str(relation["messageTime"])) == 13:
                        last_msg_date_timestamp = long(str(relation["messageTime"])[:-3])
                    else:
                        last_msg_date_timestamp = relation["messageTime"]

                    # seller_id 只有在卖家发送一条消息之后从summary中获取到，relation["childId"] 只是子账号ID 并不是loginId
                    chanel = Channel.update(
                        session, chanel, shop_id=self.shop.id, seller_id=relation["childId"],
                        seller_name=relation["childName"], buyer_id=relation["otherLoginId"],
                        buyer_name=relation["otherName"], read_stat=relation["readStat"],
                        deal_stat=relation["dealStat"], open_date="", close_date="", closed_by="",
                        flag=relation["rank"], origin_id=relation["channelId"], msg_source=msg_source, relation_type="",
                        relation_id="", last_msg_id=relation["lastMessageId"],
                        last_msg_date=time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(last_msg_date_timestamp)),
                        last_msg_content=relation["lastMessageContent"]
                    )
                    # sync_smt_customer_detail.delay(self, chanel.id, msg_source)
                    print chanel.id, chanel.seller_id, chanel.seller_name, chanel.last_msg_content
                    yield chanel.id
                if len(result["result"]) == 0:
                    break

    def sync_message_detail(self, channel_id, msg_source, current_page=1, page_size=100):
        """
        同步订单留言
        :return:
        """
        with sessionCM() as session:
            channel = Channel.find_by_id(session, channel_id)
            # if channel:
            #     print "通道id为%d, buyer_name: %s " % (channel.id, channel.buyer_name)
            additional_flag = False
            while True:
                print current_page
                result = self.msg_handler.get_msg_detail_list(channel.origin_id, msg_source, current_page, page_size)
                print json.dumps(result, indent=2, encoding='utf8')
                # raw_input("enter ... ")
                if not result["success"]:
                    return result["exception"]
                current_page += 1
                for message in result.get("result", []):
                    old_msg = Message.find_by_origin_id(session, message["id"])
                    if old_msg:
                        continue
                    print "创建新消息..."
                    Message.create(
                        session, channel_id=channel_id, origin_id=message["id"], content=message["content"],
                        image_urls=";".join([im["sPath"] for im in message["filePath"]]),
                        receive_time=time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(long(str(message["gmtCreate"])[:-3]))),
                        source="seller" if message["summary"]["senderName"] == channel.seller_name else "buyer",
                        external_message_id=""
                    )
                    print "创建消息完成 ！"
                    if additional_flag:
                        continue
                    print "设置关联关系..."
                    if not channel.relation_type or not channel.relation_id:
                        print "更新通道..."
                        Channel.update(
                            session, channel, shop_id=self.shop.id,
                            relation_type=message["messageType"],
                            relation_id=message["typeId"]
                        )
                        print "创建Attachment..."
                        Attachment.create(
                            session, channel_id=channel_id, name=message["summary"]["productName"],
                            image_url=message["summary"]["productImageUrl"], product_url=message.get("productDetailUrl", ""),  # ？？？
                            order_url=message["summary"]["orderUrl"], product_id="", order_id=""
                        )
                        channel.update(session, channel, **{})
                        additional_flag = True
                    print "设置关联完成..."
                if len(result["result"]) == 0:
                    break

    def sync_evaluation(self, ids=None):
        """
        同步评价信息
        :param ids:
        :return:
        """
        current_page = 0
        page_size = 1
        total_items = page_size

        def _execute_result(results, shop_id):
            results = results.get("listResult", [])
            with sessionCM() as session:
                for result in results:
                    evaluatioin = Evaluation.find_by_order_line_id(session, str(result.get("orderId", "")))
                    evaluatioin = Evaluation.update(
                        session, evaluation=evaluatioin,
                        order_line_item_id=str(result.get("orderId", "")),
                        shop_id=shop_id
                    )
                    print evaluatioin.order_line_item_id, evaluatioin.shop_id

        if ids:
            results = self.elt_handler.get_evaluation_list(order_ids=ids)
            _execute_result(results, self.shop.id)
        else:
            while True:
                current_page += 1
                if current_page * page_size > total_items:
                    break

                results = self.elt_handler.get_evaluation_list(current_page=current_page, page_size=page_size)
                total_items = int(results.get("totalItem", 0))
                if results["success"]:
                    _execute_result(results, self.shop.id)
                else:
                    logger.info("=" * 60)
                    logger.info(results.get("error_message"))
                    logger.info(results)
                    logger.info("=" * 60)
        pass

    def execute(self):
        logger.info("正在同步店铺ID为%d的smt客服消息" % self.shop.id)
        print("正在同步店铺ID为%d的smt客服消息" % self.shop.id)

        for channel_id in self.sync_message_list("message_center"):
            # sync_smt_customer_detail.delay(self, channel_id, "message_center")
            sync_smt_customer_detail(self, channel_id, "message_center")

        # self.sync_evaluation()

        # self.sync_message_list("message_center")
        # self.sync_message_list("order_msg")


class SyncSmtEvaluation(object):

    def __init__(self, shop, timstamp=None):
        self.shop = shop
        self.elt_handler = AliEvaluation(self.shop)

    def sync_evaluation_list(self, ids=None):
        current_page = 0
        page_size = 1
        total_items = page_size

        def _execute_result(results, shop_id):
            results = results.get("listResult", [])
            with sessionCM() as session:
                for result in results:
                    evaluatioin = Evaluation.find_by_order_line_id(session, str(result.get("orderId", "")))
                    evaluatioin = Evaluation.update(
                        session, evaluation=evaluatioin,
                        order_line_item_id=str(result.get("orderId", "")),
                        shop_id=shop_id
                    )
                    print evaluatioin.order_line_item_id, evaluatioin.shop_id

        if ids:
            results = self.elt_handler.get_evaluation_list(order_ids=ids)
            _execute_result(results, self.shop.id)
        else:
            while True:
                current_page += 1
                if current_page * page_size > total_items:
                    break

                results = self.elt_handler.get_evaluation_list(current_page=current_page, page_size=page_size)
                total_items = int(results.get("totalItem", 0))
                if results["success"]:
                    _execute_result(results, self.shop.id)
                else:
                    logger.info("=" * 60)
                    logger.info(results.get("error_message"))
                    logger.info(results)
                    logger.info("=" * 60)

    def sync_evaluation_detail(self):
        pass

    def execute(self):
        self.sync_evaluation_list()

