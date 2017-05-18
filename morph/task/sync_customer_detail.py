# -*- coding: utf-8 -*-

"""
@author: xuhe
@date: 17/5/15
@description: 
"""

import traceback
from morph.lib.utils.logger_util import logger
from morph.task import morph_celery


@morph_celery.task(ignore_result=True)
def sync_customer_detail(handler, channel_id, **kwargs):
    try:
        handler.sync_message_detail(channel_id, **kwargs)
        logger.info("%s平台编号为%s的客服通道同步成功" % ("eBay", str(channel_id)))
    except Exception, e:
        logger.error(traceback.format_exc(e))
        logger.info("%s平台编号为%s的客服通道同步失败，失败原因：%s" % (
            "eBay", str(channel_id), traceback.format_exc(e)))


@morph_celery.task(ignore_result=True)
def sync_smt_customer_detail(handler, channel_id, msg_source):
    try:
        handler.sync_message_detail(channel_id, msg_source)
        logger.info("%s平台编号为%s的客服通道同步成功" % ("AliExpress", str(channel_id)))
    except Exception, e:
        logger.error(traceback.format_exc(e))
        logger.info("%s平台编号为%s的客服通道同步失败，失败原因：%s" % (
            "AliExpress", str(channel_id), traceback.format_exc(e)))