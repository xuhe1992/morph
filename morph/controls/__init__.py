# -*- coding: utf-8 -*-

"""
@author: xuhe
@date: 17/3/30
@description: 
"""

import re
import json
import datetime
from sqlalchemy import and_
from sqlalchemy import or_
from morph.lib.model.manage import Management
from morph.lib.model.session import sessionCM
from morph.lib.model.shop import Shop
from morph.lib.model.task import Task
from morph.lib.model.channel import Channel
from morph.lib.model.message import Message
from morph.lib.model.evaluation import Evaluation


class CustomerControls(object):

    def __init__(self, user, params):
        self.user = user
        self.params = params

    def sync_customer(self):
        shops = []
        with sessionCM() as session:
            if self.params.get("shop_id"):
                shop = Shop.find_by_id(session, self.params["shop_id"])
                if not shop:
                    return {"status": 0, "message": "店铺不存在"}
                shops.append(shop.id)
            elif self.params.get("platform"):
                ms = Management.find_by_user(session, self.user.id)
                if self.params.get("platform"):
                    for m in ms:
                        if m.shop.platform != self.params["platform"]:
                            continue
                        shops.append(m.shop)
                else:
                    shops = [m.shop for m in ms]
            error_list = []
            for shop in shops:
                if shop.account == "" and shop.session == "":
                    error_list.append({"shop_id": shop.id, "message": "店铺授权失效"})
                    continue
                task = Task.find_by_shop_mold(session, shop.id, "sync_customers")
                start, end = "", datetime.datetime.now().strftime("%Y-%m-%dT%H:%M:%S")
                if not task:
                    task = Task(user_id=self.user.id, shop_id=shop.id, mold="sync_customers")
                elif task.status == 0:
                    continue
                else:
                    remark = re.sub("#[\s\S]+$", "", task.remark or "") or ";"
                    start = remark.split(";")[1]
                task.status = 0
                timestamp = "%s;%s" % (start, end)
                task_id = Task.save(session, task)
                from morph.task.sync_customer_list import sync_customer_list
                from morph.task.sync_customer_list import sync_smt_customer_list
                if shop.platform == "AliExpress":
                    sync_smt_customer_list.delay(task_id, shop.id, timestamp)
                else:
                    sync_customer_list.delay(task_id, shop.id, timestamp)
        return {"status": 1, "message": "客服消息已经开始同步，请等待同步完成", "data": error_list}

    @staticmethod
    def get_channel(shop_id, skip=0, limit=10, search=None, count=None):

        # if search:
        #     with sessionCM() as session:
        #         return session.query(Channel).filter(
        #             and_(Channel.shop_id == shop_id, Channel.buyer_name.ilike('%' + search + '%'))
        #         ).all()

        if search:
            if not isinstance(search, list):
                return []
            with sessionCM() as session:
                return session.query(Channel).filter(and_(*search)).all()

        if count:
            with sessionCM() as session:
                return session.query(Channel).filter(Channel.shop_id == shop_id).count()

        with sessionCM() as session:
            channels = session.query(Channel).filter(Channel.shop_id == shop_id). \
                order_by(Channel.last_msg_date.desc()).offset(skip).limit(limit).all()  # 最新10 个

        return channels

    @staticmethod
    def get_message(message_id=None, channel_id=None, skip=0, limit=10, count=False):

        if count and channel_id:
            with sessionCM() as session:
                return session.query(Message).filter(Message.channel_id == channel_id).count()

        if message_id:
            with sessionCM() as session:
                return Message.find_by_id(session, message_id)

        if channel_id:
            with sessionCM() as session:
                return session.query(Message).filter(Message.channel_id == channel_id).order_by(Message.receive_time) \
                    .offset(skip).limit(limit).all()

    @staticmethod
    def get_awaiting_evaluation(shop_id, skip=0, limit=10, search=None, count=None):
        with sessionCM() as session:
            if count:
                return session.query(Evaluation).filter(
                    or_(
                        and_(Evaluation.shop_id == shop_id, Evaluation.status == "seller"),
                        and_(Evaluation.shop_id == shop_id, Evaluation.status == "all")
                    )
                ).count()
            else:
                return session.query(Evaluation).filter(
                    or_(
                        and_(Evaluation.shop_id == shop_id, Evaluation.status == "seller"),
                        and_(Evaluation.shop_id == shop_id, Evaluation.status == "all")
                    )
                ).offset(skip).limit(limit).all()

    @staticmethod
    def trans_query_list(src_condition, model, cfg=None, container=list()):
        """
        将传来的条件转换为查询列表

        :param src_condition: 条件对象 {
                                            "buyer_name": "%xiao%",
                                            "read_stat": 0
                                        }表示查询 名字中带有xiao的未读的item
        :param model: 对应的查询模型
        :param cfg: 对应操作的配置，默认为channel配置
        :param container: 查询列表容器，可以预置部分内容在列表最前面
        :return:{ "status": 1/0, "data/message": "msg/list()" }
        """
        result = container
        if not cfg:
            cfg = {
                "ilike": ["seller_name", "buyer_name", "last_msg_content"],
                "equal": ["shop_id", "seller_id", "buyer_id", "read_stat",
                          "deal_stat", "flag", "msg_source", "origin_id",
                          "relation_id", "relation_type", "last_msg_id"]
            }
        if isinstance(src_condition, str):
            src_condition = json.loads(src_condition)

        def _get_eval(_model, _attr, _action, _value):
            return {
                "ilike": getattr(_model, _attr).ilike(_value),
                "equal": getattr(_model, _attr) == _value
            }[_action]

        attr_name_list = [item for item in dir(model) if not (item.startswith("__") and item.endswith("__"))]
        for item in src_condition.iter_keys():
            if item not in attr_name_list:
                return {"status": 0, "message": "Model %s :属性 %s 不存在" % (model.__name__, item)}

        for key, value in src_condition.items():
            action = ""
            for tmp_action in cfg.keys():
                if key in cfg[tmp_action]:
                    action = tmp_action
                    break
            result.append(_get_eval(model, key, action, value))
        return {"status": 1, "data": result}

