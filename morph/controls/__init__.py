# -*- coding: utf-8 -*-

"""
@author: xuhe
@date: 17/3/30
@description: 
"""

import re
import datetime
from morph.lib.model.manage import Management
from morph.lib.model.session import sessionCM
from morph.lib.model.shop import Shop
from morph.lib.model.task import Task
from morph.task.sync_customer_list import sync_customer, sync_smt_customer


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
            else:
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
                    task = Task(user_id=self.user.id, shop_id=shop.id, mold="sync_orders")
                elif task.status == 0:
                    continue
                else:
                    remark = re.sub("#[\s\S]+$", "", task.remark or "") or ";"
                    start = remark.split(";")[1]
                task.status = 0
                timestamp = "%s;%s" % (start, end)
                task_id = Task.save(session, task)
                if shop.platform == "AliExpress":
                    sync_smt_customer(task_id, shop.id, timestamp)
                else:
                    sync_customer(task_id, shop.id, timestamp)
        return {"status": 1, "message": "客服消息已经开始同步，请等待同步完成", "data": error_list}