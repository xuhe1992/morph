# -*- coding: utf-8 -*-

"""
@author: xuhe
@date: 17/5/15
@description: 
"""

import traceback
from morph.controls.ebay.sync import SyncEbayCustomer
from morph.controls.wish.sync import SyncWishCustomer
from morph.lib.utils.logger_util import logger
from morph.task import morph_celery


@morph_celery.task(ignore_result=True)
def sync_customer_detail(shop, channel_id, **kwargs):
    try:
        method_route = {
            "eBay": SyncEbayCustomer,
            "Wish": SyncWishCustomer,
        }
        handler = method_route[shop.platform](shop)
        handler.sync_message_detail(**kwargs)
        logger.info("%s平台编号为%s的客服消息通道同步成功" % (shop.platform, str(channel_id)))
    except Exception, e:
        logger.error(traceback.format_exc(e))
        logger.info("%s平台编号为%s的客服消息通道同步失败，失败原因：%s" % (
            shop.platform, str(channel_id), traceback.format_exc(e)))


@morph_celery.task(ignore_result=True)
def sync_smt_customer_detail(handler, channel_id, **kwargs):
    try:
        handler.sync_message_detail(channel_id, **kwargs)
        logger.info("%s平台编号为%s的客服通道同步成功" % ("AliExpress", str(channel_id)))
    except Exception, e:
        logger.error(traceback.format_exc(e))
        logger.info("%s平台编号为%s的客服通道同步失败，失败原因：%s" % (
            "AliExpress", str(channel_id), traceback.format_exc(e)))