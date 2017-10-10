# -*- coding: utf-8 -*-

"""
@author: xuhe
@date: 17/5/16
@description: 
"""

import datetime
import traceback
import json
from sqlalchemy import and_
from datetime import timedelta
from morph.lib.utils.logger_util import logger
from morph.lib.model.session import sessionCM
from morph.lib.model.channel import Channel
from wishsdk.ticket import WishTicket
from morph.controls.wish import WishCustomer
from morph.controls.wish.sync import SyncWishCustomer
from morph.task.sync_customer_detail import sync_customer_detail


class WishControls(WishCustomer):

    def __init__(self, shop, **kwargs):
        WishCustomer.__init__(self, **kwargs)
        self.shop = shop

    def list_channel(self):
        """
        根据参数返回回话列表

        主要是：1、返回包括最新的至少10个回话列表，
                2、根据搜索返回对应的回话列表
        :return:
        """
        data = {
            "page_no": 0,  # 当前页
            "page_total": 0,  # 总页数
            "channels": list(),  # 会话列表
            "channel_toatal": 0  # 符合查询调价的会话总数
        }

        limit = self.params.get("page_size", "") or 15
        channel_total = self.get_channel(self.shop.id, count=True)
        page_total = channel_total / limit + 1 if channel_total % limit > 0 or channel_total == 0 else channel_total/limit

        page_no = int(self.params.get("page_no", "1")) or 1
        page_no = page_total if page_no > page_total else page_no
        page_no = 1 if page_no < 1 else page_no
        skip = limit * (page_no - 1)

        channels = self.get_channel(self.shop.id, skip=skip, limit=limit)

        for channel in channels:
            item = {
                "id": str(channel.id),
                "shop_id": str(channel.shop_id),
                "buyer_id": str(channel.buyer_id),
                "buyer_name": str(channel.buyer_name),
                "read_stat": str(channel.read_stat),
                "deal_stat": str(channel.deal_stat),
                "open_date": str(channel.open_date),
                "close_date": str(channel.close_date),
                "last_msg_date": str(channel.last_msg_date),
                "last_msg_id": str(channel.last_msg_id),
                "last_msg_content": channel.last_msg_content,
            }
            data["channels"].append(item)
        data["page_no"] = page_no
        data["page_total"] = page_total
        data["channel_toatal"] = channel_total

        return {"status": 1, "data": data}

    def search_channel(self):
        """
        通过联系人名称搜索对话

        :return: 列表
        """
        search_key = self.params.get("search_key", "")
        if search_key:
            result = list()
            channels = self.get_channel(self.shop.id, search=search_key)
            for channel in channels:
                item = {
                    "id": str(channel.id),
                    "shop_id": str(channel.shop_id),
                    "buyer_id": str(channel.buyer_id),
                    "buyer_name": str(channel.buyer_name),
                    "read_stat": str(channel.read_stat),
                    "deal_stat": str(channel.deal_stat),
                    "open_date": str(channel.open_date),
                    "close_date": str(channel.close_date),
                    "last_msg_date": str(channel.last_msg_date),
                    "last_msg_id": str(channel.last_msg_id),
                    "last_msg_content": channel.last_msg_content,
                }
                result.append(item)
            return {"status": 1, "data": result}
        else:
            return {"status": 0, "data": "缺少参数：\"search_key\""}

    def list_message(self):
        """
        根据参数，返回排序的消息

        主要是：1、如果有未读消息，消息大于20条，直接返回所有未读消息，从未读第一条条消息显示
                2、如果没有未读消息或是未读消息数量小于20条，则返回排序的前20条消息，直接显示最后一条
                3、根据关键字搜索消息，返回对应的消息
        :return:
        """
        channel_id = self.params.get("channel_id", "")
        page = self.params.get("page_no", "") or 1
        limit = self.params.get("limit", "") or 10  # limit 可以是以未读消息数量为值
        limit = 10 if limit < 10 else limit
        limit = 100 if limit > 100 else limit
        if not channel_id:
            return {"status": 0, "data": "缺少参数:\"channel_id\""}
        message_total = self.get_message(count=True, channel_id=channel_id)
        page_total = message_total/limit + 1 if message_total % limit != 0 or message_total == 0 else message_total/limit
        page = page_total if page > page_total else 1 if page_total <= 0 else page
        skip = (page-1) * limit
        messages = self.get_message(channel_id=channel_id, skip=skip, limit=limit)

        tmp = list()
        for item in messages:
            tmp.append({
                "id": item.id,
                "channel_id": item.channel_id,
                "origin_id": item.origin_id,
                "reply_id": item.external_message_id,
                "content": item.content,
                "image_urls": item.image_urls,
                "receive_time": str(item.receive_time),
                "source": item.source
            })
        return {
            "status": 1,
            "data": {"page_no": page, "page_total": page_total, "message_total": message_total, "messages": tmp}
        }

    def reply_message(self):
        """
        回复消息，对应于最新一条消息的回复

        需要的参数包括：parent_message_id (被回复的消息ID) , item_id 或是 recipient_id , body
        :return:
        """
        channel_id = self.params.get("channel_id", "")
        body = self.params.get("body", "")
        with sessionCM() as session:
            channel = Channel.find_by_id(session, channel_id)
            ticket_id = channel.origin_id

        handler = WishTicket(self.shop)

        result = handler.reply_ticket_by_id(ticket_id, body)

        print "回复 Ticket ID 为 %s " % channel_id
        print result

        if result.get("success", ""):
            # 是否同步消息
            sync_handler = SyncWishCustomer(self.shop)
            sync_handler.execute(ticket_id=ticket_id)
            return {"status": 1, "message": "回复消息成功！"}
        else:
            return {"status": 0, "message": "回复消息失败！", "errors": result.get("message", "")}

    def close_ticket(self):
        """
        关闭 ticket


        :return:
        """
        ticket_id = self.params.get("channel_id", "")
        if not ticket_id:
            return {"status": 0, "message": "缺少channel_id!"}
        handler = WishTicket(self.shop)
        with sessionCM() as session:
            ticket = Channel.find_by_id(session, ticket_id)
            if not ticket:
                return {"status": 0, "message": "无效的channel_id!"}

            result = handler.close_ticket_by_id(ticket["origin_id"])

            if result.get("success", ""):
                Channel.update(session, channel=ticket, closed_by="buyer")
                return {"status": 1, "message": "已关闭！"}
            else:
                return {"status": 0, "message": result.get("message", "关闭失败！")}

    def batch_reply_message(self):
        """
        批量回复消息

        参数： ids = 123;456;789
            content = "content"
        :return:
        """
        ticket_ids = json.loads(self.params.get("ticket_ids", "[]"))
        content = self.params.get("content","")

        if not content or len(ticket_ids) == 0:
            return {"status": 0, "message": "参数不合法，检查参数！"}

        total = len(ticket_ids)
        success, failure = list(), list()

        handler = WishTicket(self.shop)

        for ticket_id in ticket_ids:
            result = handler.open_ticket_by_id(ticket_id, content)
            if result.get("success", ""):
                success.append(ticket_id)
            else:
                failure.append(ticket_id)
        if len(success) == total:
            return {"status": 1, "message": "批量发送消息成功！"}
        else:
            return {"status": 0, "message": "部分消息发送成功！", "success": success, "failure": failure}

    def update_channel_state(self):
        """
        更新 channel 的处理状态 （已处理、未处理）

        参数：channel_id --> channel 的本地Id
            state --> 状态 0表示未处理、 1表示已处理
        :return:
        """
        channel_id = self.params.get("channel_id", "")
        state = self.params.get("state", "")

        with sessionCM() as session:
            channel = Channel.find_by_id(session, channel_id)

        if not channel:
            return {"status": 0, "data": "\"channel id\"不存在！"}

        if state not in ["1", "0"]:
            return {"status": 0,  "data": "\"state\"值只能是字符串0或1！"}

        try:
            with sessionCM() as session:
                Channel.update(session, channel, {"deal_stat", int(state)})
            return {"status": 1, "data": "状态更新成功！"}
        except Exception, e:
            logger.error(traceback.format_exc(e))
            return {"status": 0, "data": "状态更新失败！"}

    def update_channel_flag(self):
        """
        更新 channel 的标签

        参数：channel_id --> channel 的本地Id
             rank --> 标志 取值 rank0,rank1,rank2,rank3,rank4,rank5
                                (白，红，橙，绿，蓝，紫)
        :return:
        """
        channel_id = self.params.get("channel_id", "")
        rank = self.params.get("rank", "")

        with sessionCM() as session:
            channel = Channel.find_by_id(session, channel_id)

        if not channel:
            return {"status": 0, "data": "\"channel_id\"不存在！"}
        if rank not in ["rank0", "rank1", "rank2", "rank3", "rank4", "rank5"]:
            return {"status": 0, "data": "\"rank\"参数的值不在合法值列表中"}

        try:
            with sessionCM() as session:
                Channel.update(session, channel, {"flag": rank})
            return {"status": 1, "data": "为channel %s 打上了 %s 标签！" % (str(channel_id), str(rank))}
        except Exception, e:
            logger.error(traceback.format_exc(e))
            return {"status": 0, "data": "打标签失败"}

    def update_channel_read(self):
        """
        更新通道为已读状态

        参数 channel_id --> channel 的本地ID
            msgSource --> 消息类型 可选参数（message_center/order_msg）
        :return:
        """
        channel_id = self.params.get("channel_id", "")

        with sessionCM() as session:
            channel = Channel.find_by_id(session, channel_id)

        if not channel:
            return {"status": 0, "data": "\"channel_id\"不存在！"}

        try:
            with sessionCM() as session:
                Channel.update(session, channel, {"read_stat", 1})
            return {"status": 1, "data": "状态更新成功！"}
        except Exception, e:
            logger.error(traceback.format_exc(e))
            return{"status": 0, "data": "状态更新失败！"}

    def appeal_to_wish_support(self):
        """
        将消息上诉给WishSupport处理

        参数仅仅需要正确的 ticket id
        :return:
        """
        ticket_id = self.params.get("ticket_id", "")
        ticket_handler = WishTicket(self.shop)
        with sessionCM() as session:
           channel = Channel.find_by_origin_id(session, ticket_id)
        if not channel:
            return {"status": 0, "data": "\"ticket_id\"不存在！"}

        result = ticket_handler.appeal_support_ticket_by_id(ticket_id=ticket_id)

        if result.get("success", ""):
            return {"status": 1, "data": "处理成功！"}
        else:
            return {"status": 0, "data": "处理失败！", "errors": result.get("message", "")}

    @staticmethod
    def store_message(channel_id, content, source, receive_time):
        pass

    @staticmethod
    def immediately_sync_message(shop):
        time_format = "%Y-%m-%dT%H:%M:%S"
        start = datetime.datetime.now() - timedelta(minutes=30)
        end = datetime.datetime.now() + timedelta(minutes=5)
        timestamp = start.strftime(time_format) + ";" + end.strftime(time_format)
        ##################
        print(shop.platform)
        print(shop.site_id)
        print(shop.account)
        print(shop.owner)
        print(shop.id)
        shop.token = "AgAAAA**AQAAAA**aAAAAA**7HTjVw**nY+sHZ2PrBmdj6wVnY+sEZ2PrA2dj6ABkoGoD5aHpAqdj6x9nY+seQ**94UCAA**AAMAAA**UGJaMLGzkw/V30Q7yrFVpkDxh9+F1v7X7taOlLW6WeEQCY/F6PhqPrjJfFLfw5rg93LNBvSQV4hO/cLtHS1K059mXzg61q4xHToNFk2uK+DdoFlCGbc1BD0TRyZ9zOSw4peeHJy/XUG2GwzkyPSrkBlU8X8e2IcZiyqCEILF0yl0ffDJy4Yz62JZVYCCX7HzvI/39N3ROGcUpCVbmxPE+QJI4a2Xst9ApBikHreVDntERITCRj8FhnnmAoDHGWziGN5GlNOQ40ETGX9GUX9yjK31haSpTpIsJRQBYhYeOYwo+F+LV5mFR55XDtuKD837jmKGZvpwll2pN4XhJfVbU7VFWbqyi2p4ccjxNEKXqmbJSSESvXmhiNK5J5EmAZVxh0BmXnNAHYCMJ1gZ7+sa4shnnzH12wcjMjK679iwXyYiK1YTrNmLNei4UeDFBfb2fzqm+eSDQIBK9g+HX/fZkTssU0O1m59wTeS+9GG6Bu7wTZyjU5cbCbjlQl6J4xhy4rs+efJLLAx/PfXmAODHgPF1Ai4rF/YYogFy+V9G0SiQJLQz31yxD3uJuDNyVoEB7/voPAvVutUvZcJzw2LAHIETfHG7GNMoHFA1fyLOF76YIZzsxBylxRY/x12gLlHFaKrtNAJRWpbKHO6usD0GMehDd9a/ALlSqHMPolKyaN6RMWEdov/Drq5PYTW+2OmO8GYyzrmCSk8s+OEv4LhLwkL4YBdYZyKoGo7Qf2FTqbfuYOKMblMi2MDACFSYKuvZ"
        shop.site_id = "0"
        ######################
        handler = SyncEbayCustomer(shop, timestamp)
        try:
            logger.info(timestamp)
            for message_dict in handler.execute():
                if not message_dict:
                    continue
                for channel_id, message_ids in message_dict.items():
                    for i in range(0, len(message_ids), 10):
                        sync_customer_detail(
                            handler.shop, channel_id,
                            message_ids=message_ids[i: i + 10]
                        )
        except Exception, e:
            logger.warning(traceback.format_exc(e))
        finally:
            pass

