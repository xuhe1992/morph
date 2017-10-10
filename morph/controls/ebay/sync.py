# -*- coding: utf-8 -*-

"""
@author: xuhe
@date: 17/3/31
@description: 
"""

import re
import datetime
from sqlalchemy import and_
from ebaysdk.trading.message import EbayMessage
from ebaysdk.trading.evaluation import EbayEvaluation
from morph.lib.model.attachment import Attachment
from morph.lib.model.channel import Channel
from morph.lib.model.evaluation import Evaluation
from morph.lib.model.message import Message
from morph.lib.model.session import sessionCM
from morph.lib.utils.logger_util import logger


class SyncEbayCustomer(object):

    def __init__(self, shop, timestamp=None):
        self.shop = shop
        self.timestamp = timestamp
        self.msg_handler = EbayMessage(shop.site_id, shop.account)
        self.elt_handler = EbayEvaluation(shop.site_id, shop.account)

    def sync_message_list(self):
        # 第一步：获取所有消息文件夹
        start, end = self.timestamp.split(";")
        end = datetime.datetime.strptime(end, "%Y-%m-%dT%H:%M:%S")  # - datetime.timedelta(days=1)
        if not start:
            start = end - datetime.timedelta(days=365)
        else:
            start = datetime.datetime.strptime(start, "%Y-%m-%dT%H:%M:%S")  # - datetime.timedelta(days=1)
            start = start.strftime("%Y-%m-%dT%H:%M:%S")
            end = end.strftime("%Y-%m-%dT%H:%M:%S")
        logger.info("eBay-%d:正在获取FolderSummary" % self.shop.id)
        print("eBay-%d:正在获取FolderSummary" % self.shop.id)
        result = self.msg_handler.get_my_messages("ReturnSummary", start_time=start, end_time=end)
        print result, type(result)
        # 第二步：获取每个文件夹下的Message简要信息，从而获取MessageIDs
        for summary in result["Summary"]["FolderSummary"]:
            logger.info("eBay-%d:正在获取FolderID为%s的MessageList" % (self.shop.id, summary["FolderID"]))
            print("eBay-%d:正在获取FolderID为%s的MessageList" % (self.shop.id, summary["FolderID"]))
            if summary["FolderID"] == "2":
                continue
            yield self._get_messages_in_folder(summary["FolderID"], start, end)
            logger.info("eBay-%d:FolderID为%s的MessageList同步完成" % (self.shop.id, summary["FolderID"]))
            print ("eBay-%d:FolderID为%s的MessageList同步完成" % (self.shop.id, summary["FolderID"]))
            logger.info("-" * 30)
            print ("-" * 30)

    def _get_messages_in_folder(self, folder_id, start, end, current_page=1, page_size=200):
        seller_id = self.shop.owner
        with sessionCM() as session:
            message_dict = dict()
            while True:
                logger.info("eBay-%d:正在同步第%d页的MessageList" % (self.shop.id, current_page))
                print ("eBay-%d:正在同步第%d页的MessageList" % (self.shop.id, current_page))
                result = self.msg_handler.get_my_messages(
                    "ReturnHeaders", folder_id=folder_id, start_time=start, end_time=end,
                    current_page=current_page, page_size=page_size)
                print result
                if not result["Messages"]:
                    break
                message_list = result["Messages"]["Message"]
                if not isinstance(message_list, list):
                    message_list = [message_list]
                for header in message_list:
                    read_stat, deal_stat = True, True
                    if header["Sender"] == seller_id:
                        seller_name, buyer_id, buyer_name = seller_id, header["SendToName"], header["SendToName"]
                    else:
                        seller_name, buyer_id, buyer_name = seller_id, header["Sender"], header["Sender"]
                        read_stat = header["Read"] == "true"  # ??
                        deal_stat = header["Replied"] == "true"  # ??

                    channel = Channel.find_by_channel_composition(session, seller_id, buyer_id, header.get("ItemID", 0))
                    # header中包含来自eBay的消息，该消息不一定拥有ItemID字段，取默认值0
                    receive_date = datetime.datetime.strptime(
                        header["ReceiveDate"].rsplit(".", 1)[0], "%Y-%m-%dT%H:%M:%S")
                    if channel:
                        kwargs = dict()
                        if receive_date > channel.last_msg_date:
                            kwargs["last_msg_date"] = receive_date
                            kwargs["last_msg_id"] = header["MessageID"]
                        if receive_date < channel.open_date:
                            kwargs["open_date"] = receive_date
                        # 更新channel状态
                        # kwargs["read_stat"] = channel.read_stat and read_stat
                        # kwargs["deal_stat"] = channel.deal_stat and deal_stat
                        Channel.update(session, channel, **kwargs)
                    else:
                        channel = Channel.create(
                            session, shop_id=self.shop.id, seller_id=seller_id, seller_name=seller_name,
                            buyer_id=buyer_id, buyer_name=buyer_name, read_stat=read_stat,
                            deal_stat=deal_stat, flag="rank0" if header["Flagged"] == "true" else "",
                            msg_source="from ebay" if buyer_id == "eBay" else "from members",
                            relation_id=header.get("ItemID", 0), relation_type="product", origin_id=0,
                            open_date=receive_date, last_msg_date=receive_date, last_msg_id=header["MessageID"],
                            last_msg_content="同步中..."
                        )
                        product_url = "http://www.ebay.com/itm/%s" % header.get("ItemID", 0)
                    # if not channel:  # ???
                        Attachment.create(
                            session, channel_id=channel.id,
                            name=header.get("ItemTitle", ""), product_url=product_url,
                            product_id=header.get("ItemID", "0"), image_url="",
                            order_id="", order_url=""
                        )
                    if not message_dict.get(channel.id):
                        message_dict[channel.id] = list()
                    message_dict[channel.id].append(header["MessageID"])
                if len(message_list) < page_size:
                    break
                current_page += 1
        return message_dict

    def sync_message_detail(self, channel_id, **kwargs):
        # 第三步获取Message的详细信息
        # 首先删除此管道中已经发送的消息， 查询参数：channel_id original_id=async
        message_ids = kwargs["message_ids"]
        result = self.msg_handler.get_my_messages("ReturnMessages", message_ids=message_ids)
        txt_pattern = re.compile('<div id="UserInputtedText">([\s\S]+?)</div>')
        pic_pattern = re.compile('<img id="previewimage\d+".+?src="(.+?)">')
        href_pattern = re.compile('(<a[^>]+?)>')
        with sessionCM() as session:
            channel = Channel.find_by_id(session, channel_id)
            # 清除‘异步消息’
            session.query(Message).filter(and_(Message.channel_id == channel.id, Message.origin_id == 'async')).delete()
            message_list = result["Messages"]["Message"]
            if not isinstance(message_list, list):
                message_list = [message_list]
            for message in message_list:
                # if Message.find_by_origin_id(session, message["MessageID"]):
                #     continue
                if message["Sender"] == "eBay":
                    href_rs = href_pattern.findall(message["Text"])
                    for href in href_rs:
                        message["Text"] = message["Text"].replace(href, href + ' target="_blank"')
                    print "创建 Ebay Message ..."
                    Message.create(
                        session, channel_id=channel_id, origin_id=message["MessageID"],
                        image_urls="", content=message["Text"], source="ebay", external_message_id="",
                        receive_time=message["ReceiveDate"].rsplit(".", 1)[0],
                    )
                    print "创建 Ebay Message 完成！"
                else:
                    txt_rs = txt_pattern.findall(message["Text"])
                    content = txt_rs[0] if txt_rs else ""
                    pic_rs = pic_pattern.findall(message["Text"])
                    print "创建普通消息 ..."
                    Message.create(
                        session, channel_id=channel_id, origin_id=message["MessageID"],
                        image_urls=";".join(pic_rs), content=content,
                        receive_time=message["ReceiveDate"].rsplit(".", 1)[0],
                        external_message_id=message.get("ExternalMessageID", ""),
                        source="seller" if message["Sender"] == channel.seller_id else "buyer"
                    )
                    print "创建普通消息完成！"
                    if message["MessageID"] == channel.last_msg_id:  # ??
                        Channel.update(session, channel, last_msg_content=content)

    def sync_awaiting_evaluation_list(self):
        total_page = 1
        current_page = 0
        page_size = 100
        while True:
            current_page += 1
            logger.info("current_page: %d " % current_page)
            logger.info("total_page: %d " % total_page)
            if current_page > total_page:
                break

            result = self.elt_handler.get_awaiting_feedback(current_page=current_page, page_size=page_size)
            # print result
            if result.get("Ack") == "Success":
                items_awaiting_feed_back = result["ItemsAwaitingFeedback"]
                # print items_awaiting_feed_back
                total_page = int(items_awaiting_feed_back["PaginationResult"]["TotalNumberOfPages"])
                print "tmp_total_page: %s " % total_page
                if not int(total_page):
                    break
                transactions = items_awaiting_feed_back["TransactionArray"]["Transaction"]
                if isinstance(transactions, dict):
                    transactions = [transactions]

                with sessionCM() as session:
                    for transaction in transactions:
                        t_item = transaction.get("Item", {})
                        buyer = transaction.get("Buyer", {})
                        if transaction.get("FeedbackReceived", ""):
                            status = "seller"
                        elif transaction.get("FeedbackLeft", ""):
                            status = "buyer"
                        else:
                            status = "all"

                        evaluation = Evaluation.find_by_order_line_id(session, transaction["OrderLineItemID"])
                        kw = {
                            "shop_id": self.shop.id,
                            "order_line_item_id": transaction["OrderLineItemID"],
                            "item_id": t_item.get("ItemID", ""),
                            "item_title": t_item.get("Title", ""),
                            "status": status,
                            "buyer_id": buyer.get("UserID", ""),
                            "seller_content": ""
                        }
                        evaluation = Evaluation.update(session, evaluation, **kw)
                        # print '-'*60
                        # print evaluation.id, evaluation.buyer_id, evaluation.status, evaluation.order_line_item_id
                        # print evaluation.item_id, evaluation.item_title, evaluation.seller_content
        print "同步完成！"

    def sync_awaiting_evaluation_detail(self):
        pass

    def sync_today(self):
        from morph.task.sync_customer_detail import sync_customer_detail
        logger.info("正在同步店铺ID为%d的eBay客服消息" % self.shop.id)
        print("正在同步店铺ID为%d的eBay客服消息" % self.shop.id)

        for message_dict in self.sync_message_list():
            if not message_dict:
                continue
            for channel_id, message_ids in message_dict.iteritems():
                for i in xrange(0, len(message_ids), 10):
                    sync_customer_detail(
                        self, channel_id,
                        message_ids=message_ids[i: i + 10]
                    )

    def execute(self):
        from morph.task.sync_customer_detail import sync_customer_detail
        logger.info("正在同步店铺ID为%d的eBay客服消息" % self.shop.id)
        print("正在同步店铺ID为%d的eBay客服消息" % self.shop.id)
        for message_dict in self.sync_message_list():
            if not message_dict:
                continue
            for channel_id, message_ids in message_dict.items():
                for i in xrange(0, len(message_ids), 10):
                    # sync_customer_detail.delay(
                    sync_customer_detail(
                        self.shop, channel_id,
                        message_ids=message_ids[i: i + 10]
                    )


        # for result in self.sync_message_list():
        #     yield result

        logger.info("正在同步店铺ID为%d的eBay评价" % self.shop.id)
        # self.sync_awaiting_evaluation_list()
        logger.info("同步店铺ID为%d的eBay评价完成！" % self.shop.id)


class SyncEbayEvaluation(object):

    def __init__(self, shop):
        self.shop = shop
        self.elt_handler = EbayEvaluation(shop.site_id, shop.account)

    def sync_awaiting_evaluation_list(self):
        total_page = 1
        current_page = 0
        page_size = 100
        print "开始同步 ... "
        while True:
            current_page += 1
            print "current_page: %d " % current_page
            print "total_pageL %d " % total_page
            if current_page > total_page:
                import time
                time.sleep(3)
                break

            result = self.elt_handler.get_awaiting_feedback(current_page=current_page, page_size=page_size)
            # print result
            if result.get("Ack") == "Success":
                items_awaiting_feed_back = result["ItemsAwaitingFeedback"]
                # print items_awaiting_feed_back
                total_page = int(items_awaiting_feed_back["PaginationResult"]["TotalNumberOfPages"])
                print "tmp_total_page: %s " % total_page
                if not int(total_page):
                    break
                transactions = items_awaiting_feed_back["TransactionArray"]["Transaction"]
                if isinstance(transactions, dict):
                    transactions = [transactions]

                with sessionCM() as session:
                    for transaction in transactions:
                        t_item = transaction.get("Item", {})
                        buyer = transaction.get("Buyer", {})
                        if transaction.get("FeedbackReceived", ""):
                            status = "seller"
                        elif transaction.get("FeedbackLeft", ""):
                            status = "buyer"
                        else:
                            status = "all"

                        evaluation = Evaluation.find_by_order_line_id(session, transaction["OrderLineItemID"])
                        kw = {
                            "shop_id": self.shop.id,
                            "order_line_item_id": transaction["OrderLineItemID"],
                            "item_id": t_item.get("ItemID", ""),
                            "item_title": t_item.get("Title", ""),
                            "status": status,
                            "buyer_id": buyer.get("UserID", ""),
                            "seller_content": ""
                        }
                        evaluation = Evaluation.update(session, evaluation, **kw)
                        print '-'*60
                        print evaluation.id, evaluation.buyer_id, evaluation.status, evaluation.order_line_item_id
                        print evaluation.item_id, evaluation.item_title, evaluation.seller_content
        print "同步完成！"

    def sync_awaiting_evaluation_detail(self):
        pass

    def execute(self):
        self.sync_awaiting_evaluation_list()
