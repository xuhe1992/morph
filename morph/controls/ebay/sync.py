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
from morph.lib.model.session import sessionCM
from morph.lib.model.message import Message
from morph.lib.utils.logger_util import logger
from morph.task.sync_customer_detail import sync_customer_detail


class SyncEbayCustomer(object):

    def __init__(self, shop, timestamp):
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
            if summary["FolderID"] == "2":
                continue
            self._get_messages_in_folder(summary["FolderID"], start, end)

    def _get_messages_in_folder(self, folder_id, start, end, current_page=1, page_size=200):
        seller_id = self.shop.owner
        with sessionCM() as session:
            message_ids = list()
            while True:
                result = self.msg_handler.get_my_messages(
                    "ReturnHeaders", folder_id=folder_id, start_time=start, end_time=end,
                    current_page=current_page, page_size=page_size)
                for header in result["Messages"]["Message"]:
                    read_stat, deal_stat = True, True
                    if header["Sender"] == seller_id:
                        seller_name, buyer_id, buyer_name = seller_id, header["SendToName"], header["SendToName"]
                    else:
                        seller_name, buyer_id, buyer_name = seller_id, header["Sender"], header["Sender"]
                        read_stat = header["Read"] == "true"
                        deal_stat = header["Replied"] == "true"
                    channel = Channel.find_by_channel_composition(session, seller_id, buyer_id, header.get("ItemID", 0))
                    Channel.update(
                        session, channel, shop_id=self.shop.id, seller_id=seller_id, seller_name=seller_name,
                        buyer_id=buyer_id, buyer_name=buyer_name, read_stat=read_stat,
                        deal_stat=deal_stat, flag="rank0" if header["Flagged"] == "true" else "",
                        msg_source="from ebay" if buyer_id == "eBay" else "from members",
                        relation_id=header["ItemID"], relation_type="product"
                    )
                    product_url = "http://www.ebay.com/itm/%s" % header["ItemID"]
                    if not channel:
                        Attachment.create(
                            session, channel_id=channel.id,
                            name=header["ItemTitle"], product_url=product_url
                        )
                    message_ids.append(header["MessageID"])
                    if len(message_ids) == 10:
                        sync_customer_detail.delay(self, channel.id, message_ids=message_ids)
                        message_ids = list()

    def sync_message_detail(self, channel_id, **kwargs):
        # 第三步获取Message的详细信息
        message_ids = kwargs["message_ids"]
        result = self.msg_handler.get_my_messages("ReturnMessages", message_ids=message_ids)
        txt_pattern = re.compile('<div id="UserInputtedText">([\s\S]+?)</div>')
        pic_pattern = re.compile('<img id="previewimage\d+".+?src="(.+?)">')
        href_pattern = re.compile('(<a[^>]+?)>')
        with sessionCM() as session:
            for message in result["Messages"]["Message"]:
                old_msg = Message.find_by_origin_id(session, message["MessageID"])
                if old_msg:
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

    def execute(self):
        logger.info("正在同步店铺ID为%d的eBay客服消息" % self.shop.id)
        self.sync_message_list()
        logger.info("店铺ID为%d的eBay客服消息同步完成" % self.shop.id)
