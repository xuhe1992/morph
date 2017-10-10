# -*- coding: utf-8 -*-

"""
@author: xuhe
@date: 17/3/31
@description: 
"""
import hashlib
import time
import datetime
from wishsdk.ticket import WishTicket
from morph.lib.model.channel import Channel
from morph.lib.model.session import sessionCM
from morph.lib.model.message import Message
from morph.lib.model.shop import Shop


class SyncWishCustomer(object):

    def __init__(self, shop):
        self.shop = shop

    def sync_ticket_list(self, current_page=0, page_size=500, ticket_id=None):
        handler = WishTicket(self.shop)
        shop_id = self.shop.id

        def _deal_with_result(datas):
            if isinstance(datas, dict):
                datas = [datas]
            print "处理Ticket ... "
            for ticket in datas:
                print ticket
                ticket = ticket["Ticket"]
                print shop_id
                kw = {
                    "shop_id": shop_id, "seller_id": ticket["merchant_id"], "seller_name": "",
                    "buyer_id": ticket["UserInfo"]["id"], "buyer_name": ticket["UserInfo"]["name"],
                    "read_stat": "0", "deal_stat":0 if ticket["state_id"] == '4' else 1,
                    "open_date": ticket["open_date"], "close_date": ticket.get("close-date", ""),
                    "closed_by": "", "flag": "", "msg_source": "", "origin_id": ticket["id"],
                    "relation_id": ticket["transaction_id"], "relation_type": "transaction",
                    "last_msg_date": ticket["last_update_date"], "last_msg_id": "",
                    "last_msg_content": ticket["subject"] + ";" + ticket["sublabel"]
                }
                with sessionCM() as session:
                    channel = Channel.find_by_origin_id(session, ticket["id"])
                    print "更新/生成Ticket ... "
                    channel = Channel.update(session, channel, **kw)
                    print "更新Replies ... "
                    # 直接同步消息内容
                    self.sync_message_detail(channel, ticket["replies"])
                    print "更新Replies 完成！"

        if ticket_id:
            print "获取单个Ticket ... "
            result = handler.retrieve_ticket_by_id(ticket_id)
            print "获取完成 ... "
            # 对 ticket进行处理
            _deal_with_result(result.get("data")) if len(result.get("data", [])) > 0 else ""
        else:
            while True:
                result = handler.list_all_tickets(start=current_page, limit=page_size)
                datas = result.get("data", [])
                if not len(datas):
                    break
                current_page += len(datas)
                _deal_with_result(datas)

    @staticmethod
    def sync_message_detail(channel, replies):
        latest_date = datetime.datetime(1970, 1, 1)
        is_first_sync = True  # 第一次同步直接记录所有信息，根据是否有这个 ticket 的信息
        with sessionCM() as session:
            tmp_msgs = session.query(Message).filter(Message.channel_id == channel.id).all()
            if tmp_msgs:
                date_list = [time.strptime("%Y-%m-%d %H:%M:%s", item.receive_time) for item in tmp_msgs]
                latest_date = max(date_list)
                is_first_sync = False

            for reply in replies:
                reply = reply["Reply"]
                msg_date = reply['date']
                msg_timestamp = time.strptime("%Y-%m-%dT%H:%M:%s", msg_date)
                if not is_first_sync and msg_timestamp <= latest_date:
                    continue
                print "创建 Message ... "
                Message.create(
                    session, channel_id=channel.id, origin_id="", external_message_id="",
                    content=reply["message"], image_urls=";".join(reply["image_urls"]),
                    receive_time=reply["date"], source="buyer" if reply["sender"] == "user" else "seller",
                )
                latest_date = time.strptime("%Y-%m-%dT%H:%M:%s", reply["date"])
                print "创建完成 ！ "

    def execute(self, ticket_id=None):
        self.sync_ticket_list(ticket_id=ticket_id)


if __name__ == '__main__':
    shop = Shop()
    shop.account = '373756ae5115474c8f0bcba44159194a'
    shop.platform = "Wish"
    shop.id = 7104
    handler = SyncWishCustomer(shop)
    print "开始同步 ... "
    handler.execute()
    print "同步完成 ! "
