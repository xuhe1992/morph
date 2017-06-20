# -*- coding: utf-8 -*-

"""
@author: xuhe
@date: 17/3/31
@description: 
"""

import re
import datetime
from ebaysdk.trading.message import EbayMessage
from ebaysdk.trading.evaluation import EbayEvaluation
from morph.lib.model.attachment import Attachment
from morph.lib.model.channel import Channel
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
        if not start:
            start, end = None, None
        else:
            start = datetime.datetime.strptime(start, "%Y-%m-%dT%H:%M:%S") - datetime.timedelta(days=1)
            end = datetime.datetime.strptime(end, "%Y-%m-%dT%H:%M:%S") - datetime.timedelta(days=1)
            start = start.strftime("%Y-%m-%dT%H:%M:%S")
            end = end.strftime("%Y-%m-%dT%H:%M:%S")
        result = self.msg_handler.get_my_messages("ReturnSummary", start_time=start, end_time=end)
        # 第二步：获取每个文件夹下的Message简要信息，从而获取MessageIDs
        for summary in result["Summary"]["FolderSummary"]:
            logger.info("eBay-%d:正在获取FolderID为%s的MessageList" % (self.shop.id, summary["FolderID"]))
            if summary["FolderID"] == "2":
                continue
            yield self._get_messages_in_folder(summary["FolderID"], start, end)
            logger.info("eBay-%d:FolderID为%s的MessageList同步完成" % (self.shop.id, summary["FolderID"]))
            logger.info("-" * 30)

    def _get_messages_in_folder(self, folder_id, start, end, current_page=1, page_size=200):
        seller_id = self.shop.owner
        with sessionCM() as session:
            message_dict = dict()
            while True:
                logger.info("eBay-%d:正在同步第%d页的MessageList" % (self.shop.id, current_page))
                result = self.msg_handler.get_my_messages(
                    "ReturnHeaders", folder_id=folder_id, start_time=start, end_time=end,
                    current_page=current_page, page_size=page_size)
                if not result["Messages"]:
                    break
                for header in result["Messages"]["Message"]:
                    read_stat, deal_stat = True, True
                    if header["Sender"] == seller_id:
                        seller_name, buyer_id, buyer_name = seller_id, header["SendToName"], header["SendToName"]
                    else:
                        seller_name, buyer_id, buyer_name = seller_id, header["Sender"], header["Sender"]
                        read_stat = header["Read"] == "true"
                        deal_stat = header["Replied"] == "true"
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
                    if not channel:
                        Attachment.create(
                            session, channel_id=channel.id,
                            name=header["ItemTitle"], product_url=product_url
                        )
                    if not message_dict.get(channel.id):
                        message_dict[channel.id] = list()
                    message_dict[channel.id].append(header["MessageID"])
                current_page += 1
        return message_dict

    def sync_message_detail(self, channel_id, **kwargs):
        # 第三步获取Message的详细信息
        message_ids = kwargs["message_ids"]
        result = self.msg_handler.get_my_messages("ReturnMessages", message_ids=message_ids)
        txt_pattern = re.compile('<div id="UserInputtedText">([\s\S]+?)</div>')
        pic_pattern = re.compile('<img id="previewimage\d+".+?src="(.+?)">')
        href_pattern = re.compile('(<a[^>]+?)>')
        with sessionCM() as session:
            channel = Channel.find_by_id(session, channel_id)
            message_list = result["Messages"]["Message"]
            if not isinstance(message_list, list):
                message_list = [message_list]
            for message in message_list:
                if Message.find_by_origin_id(session, message["MessageID"]):
                    continue
                if message["Sender"] == "eBay":
                    href_rs = href_pattern.findall(message["Text"])
                    for href in href_rs:
                        message["Text"] = message["Text"].replace(href, href + ' target="_blank"')
                    Message.create(
                        session, channel_id=channel_id, origin_id=message["MessageID"],
                        image_urls="", content=message["Text"],
                        receive_time=message["ReceiveDate"].rsplit(".", 1)[0]
                    )
                else:
                    txt_rs = txt_pattern.findall(message["Text"])
                    content = txt_rs[0] if txt_rs else ""
                    pic_rs = pic_pattern.findall(message["Text"])
                    Message.create(
                        session, channel_id=channel_id, origin_id=message["MessageID"],
                        image_urls=";".join(pic_rs), content=content,
                        receive_time=message["ReceiveDate"].rsplit(".", 1)[0]
                    )
                    if message["MessageID"] == channel.last_msg_id:
                        Channel.update(session, channel, last_msg_content=content)

    def execute(self):
        logger.info("正在同步店铺ID为%d的eBay客服消息" % self.shop.id)
        for result in self.sync_message_list():
            yield result
