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
from ebaysdk.trading.message import EbayMessage
from ebaysdk.trading.evaluation import EbayEvaluation
from morph.lib.model.session import sessionCM
from morph.lib.model.channel import Channel
from morph.lib.model.message import Message
from morph.lib.model.evaluation import Evaluation
from morph.controls.ebay import EbayCustomer
from morph.controls.ebay.sync import SyncEbayCustomer


class EbayControls(EbayCustomer):

    def __init__(self, shop, **kwargs):
        EbayCustomer.__init__(self, **kwargs)
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

        limit = int(self.params.get("page_size", 15))
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
        search_key = json.loads(self.params.get("search_key", "{}"))
        if search_key:
            result = list()
            query_list = [getattr(Channel, 'shop_id') == self.shop.id]
            query_list = self.trans_query_list(search_key, Channel, container=query_list)
            channels = self.get_channel(self.shop.id, search=query_list)
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
        limit = self.params.get("page_size", "") or 10  # limit 可以是以未读消息数量为值
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
        parent_message_id = self.params.get("parent_message_id", "")
        channel_id = self.params.get("channel_id", "")
        # recipient_id = self.params.get("recipient_id", "")
        body = self.params.get("body", "")
        with sessionCM() as session:
            channel = Channel.find_by_id(session, channel_id)
            if not channel:
                return {"status": 0, "message": "无效的channel_id!"}

        handler = EbayMessage(self.shop.site_id, self.shop.account)

        result = handler.add_message_rtq(
            parent_message_id=parent_message_id, item_id=channel.relation_id,
            recipient_id=channel.buyer_id, body=body
        )
        print parent_message_id, channel.relation_id, channel.buyer_id, body
        print result
        if result.get("Ack", "") == "Success":
            # 同步消息
            with sessionCM() as session:
                Message.create(
                    session, channel_id=channel.id, origin_id='async',
                    content=body, image_urls="", receive_time=datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                    source='seller', external_message_id=''
                )
            return {"status": 1, "message": "回复消息成功！"}
        else:
            return {"status": 0, "message": "回复消息失败！", "errors": result.get("Errors", "")}

    def batch_reply_message(self):
        """
        批量回复消息

        :return:
        """
        replys = json.loads(self.params.get("replys", "[]"))
        handler = EbayMessage(self.shop.site_id, self.shop.account)
        total = len(replys)
        success = []
        failure = []
        with sessionCM() as session:
            for reply in replys:
                result = handler.add_message_rtq(
                    parent_message_id=reply["parent_message_id"], item_id=reply["item_id"],
                    recipient_id=reply["recipient_id"], body=reply["body"]
                )
                if result.get("Ack", "") == "Success":
                    success.append(reply)
                else:
                    failure.append(reply)

        if len(success) == total:
            return {"status": 1, "message": "批量回复完成！"}
        else:
            return {"status": 0, "message": "部分回复成功！", "success": success, "failure": failure}

    def list_evaluation(self):
        data = {
            "page_no": 0,  # 当前页
            "page_total": 0,  # 总页数
            "evaluations": list(),  # 会话列表
            "evaluation_toatal": 0  # 符合查询调价的会话总数
        }

        limit = 15
        evaluation_total = self.get_awaiting_evaluation(self.shop.id, count=True)
        page_total = evaluation_total / limit + 1 if evaluation_total % limit > 0 or evaluation_total == 0 else evaluation_total / limit

        page_no = int(self.params.get("page_no", "1")) or 1
        page_no = page_total if page_no > page_total else page_no
        page_no = 1 if page_no < 1 else page_no
        skip = limit * (page_no - 1)

        evaluations = self.get_awaiting_evaluation(self.shop.id, skip=skip, limit=limit)

        for evaluation in evaluations:
            item = {
                "id": str(evaluation.id),
                "shop_id": str(evaluation.shop_id),
                "buyer_id": str(evaluation.buyer_id),
                "status": str(evaluation.status),
                "item_id": str(evaluation.item_id),
                "order_line_item_id": str(evaluation.order_line_item_id),
                "item_title": evaluation.item_title
            }
            data["evaluations"].append(item)
        data["page_no"] = page_no
        data["page_total"] = page_total
        data["evaluation_toatal"] = evaluation_total
        return {"status": 1, "data": data}

    def leave_evaluation(self):
        """
        留下评价

        测试的时候 注意是否需要评分
        :return:
        """
        evaluation_id = self.params.get("evaluation_id", "")
        content = self.params.get("content", "")
        handler = EbayEvaluation(self.shop.site_id, self.shop.account)

        if not evaluation_id:
            return {"status": 0, "message": "缺少evaluation_id！"}
        if not content:
            return {"status": 0, "message": "缺少评价内容！"}

        with sessionCM() as session:
            evaluation = Evaluation.find_by_id(session, evaluation_id)
            if not evaluation:
                return {"status": 0, "message": "该评价不存在，无法回复！"}

            result = handler.leave_feedback(
                content, evaluation.buyer_id, item_id=evaluation.order_line_item_id.split('-')[0],
                order_line_item_id=evaluation.order_line_item_id, transaction_id=evaluation.order_line_item_id.split("-")[1]
            )

            if result.get("Ack", "") == "Success":
                Evaluation.update(session, evaluation, seller_content=content)
                return {"status": 1, "message": "评价成功！"}
            else:
                return {"status": 0, "message": "评价失败！", "errors": result.get("Errors", "")}

    def batch_leave_evaluation(self):
        """
        批量留下评价

        :return:
        """
        evaluation_ids = json.loads(self.params.get("evaluation_ids", "[]"))
        content = self.params.get("content", "")
        handler = EbayEvaluation(self.shop.site_id, self.shop.account)
        total = len(evaluation_ids)
        success, failure = list(), list()
        if not evaluation_ids:
            return {"status": 0, "message": "缺少evaluation_ids！"}
        if not content:
            return {"status": 0, "message": "缺少评价内容！"}

        with sessionCM() as session:
            for evaluation_id in evaluation_ids:
                evaluation = Evaluation.find_by_id(session, evaluation_id)
                if not evaluation:
                    failure.append(evaluation_id)
                    continue

                result = handler.leave_feedback(
                    content, evaluation.buyer_id, item_id=evaluation.order_line_item_id.split('-')[0],
                    order_line_item_id=evaluation.order_line_item_id, transaction_id=evaluation.order_line_item_id.split("-")[1]
                )

                if result.get("Ack", "") == "Success":
                    Evaluation.update(session, evaluation, seller_content=content)
                    success.append(evaluation_id)
                else:
                    failure.append(evaluation_id)
        if len(success) == total:
            return {"status": 1, "message": "批量留评完成！"}
        else:
            return {"status": 0, "message": "部分留评成功！", "success": success, "failure": failure}

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
            return {"status": 0, "message": "\"channel id\"不存在！"}

        if state not in ["1", "0"]:
            return {"status": 0,  "message": "\"state\"值只能是字符串0或1！"}

        try:
            with sessionCM() as session:
                Channel.update(session, channel, {"deal_stat", int(state)})
            return {"status": 1, "message": "状态更新成功！"}
        except Exception, e:
            logger.error(traceback.format_exc(e))
            return {"status": 0, "message": "状态更新失败！"}

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
            return {"status": 0, "message": "\"channel_id\"不存在！"}
        if rank not in ["rank0", "rank1", "rank2", "rank3", "rank4", "rank5"]:
            return {"status": 0, "message": "\"rank\"参数的值不在合法值列表中"}

        try:
            with sessionCM() as session:
                Channel.update(session, channel, {"flag": rank})
            return {"status": 1, "message": "为channel %s 打上了 %s 标签！" % (str(channel_id), str(rank))}
        except Exception, e:
            logger.error(traceback.format_exc(e))
            return {"status": 0, "message": "打标签失败"}

    def update_channel_read(self):
        """
        更新通道为已读状态

        参数 channel_id --> channel 的本地ID
            msgSource --> 消息类型 可选参数（message_center/order_msg）
        :return:
        """
        channel_id = self.params.get("channel_id", "")
        read_state = self.params.get("read_state")
        with sessionCM() as session:
            channel = Channel.find_by_id(session, channel_id)

        if not channel:
            return {"status": 0, "data": "\"channel_id\"不存在！"}

        try:
            with sessionCM() as session:
                if int(read_state) in [0, 1]:
                    Channel.update(session, channel, {"read_stat", int(read_state)})
            return {"status": 1, "data": "状态更新成功！"}
        except Exception, e:
            logger.error(traceback.format_exc(e))
            return{"status": 0, "data": "状态更新失败！"}

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
                        pass
                        # sync_customer_detail(
                        #     handler.shop, channel_id,
                        #     message_ids=message_ids[i: i + 10]
                        # )
        except Exception, e:
            logger.warning(traceback.format_exc(e))
        finally:
            pass


