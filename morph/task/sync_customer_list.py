# -*- coding: utf-8 -*-

"""
@author: xuhe
@date: 17/3/31
@description: 
"""

import traceback
from morph.controls.ebay.sync import SyncEbayCustomer
from morph.controls.smt.sync import SyncSmtCustomer
from morph.controls.wish.sync import SyncWishCustomer
from morph.lib.model.session import sessionCM
from morph.lib.model.shop import Shop
from morph.lib.model.task import Task
from morph.lib.utils.logger_util import logger
from morph.task import morph_celery
from morph.task.sync_customer_detail import sync_customer_detail


@morph_celery.task(ignore_result=True)
def sync_customer_list(task_id, shop_id, timestamp):
    method_route = {
        "eBay": SyncEbayCustomer,
        "Wish": SyncWishCustomer,
    }
    with sessionCM() as session:
        task = Task.find_by_id(session, task_id)
        shop = Shop.find_by_id(session, shop_id)
        handler = method_route[shop.platform](shop, timestamp)
        try:
            logger.info(timestamp)
            for message_dict in handler.execute():
                if not message_dict:
                    continue
                for channel_id, message_ids in message_dict.items():
                    for i in range(0, len(message_ids), 10):
                        sync_customer_detail.delay(
                            handler.shop, channel_id,
                            message_ids=message_ids[i: i+10]
                        )
            task.status = 1
            task.remark = timestamp
        except Exception, e:
            logger.warning(traceback.format_exc(e))
            task.status = -1
        finally:
            Task.update(session, task)


@morph_celery.task(ignore_result=True)
def sync_smt_customer_list(task_id, shop_id, timestamp):
    with sessionCM() as session:
        task = Task.find_by_id(session, task_id)
        shop = Shop.find_by_id(session, shop_id)
        handler = SyncSmtCustomer(shop, timestamp)
        try:
            logger.info(timestamp)
            handler.execute()
            task.status = 1
            task.remark = timestamp
        except Exception, e:
            logger.warning(traceback.format_exc(e))
            task.status = -1
        finally:
            Task.update(session, task)
