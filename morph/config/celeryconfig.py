# -*- coding: utf-8 -*-

"""
@author: xuhe
@date: 17/5/18
@description: 
"""


CELERY_DEFAULT_QUEUE = "default_queue"
CELERY_DEFAULT_EXCHANGE_TYPE = "direct"
CELERY_DEFAULT_ROUTING_KEY = "default.queue"
CELERY_PREFETCH_MULTIPLIER = 1
CELERY_IGNORE_RESULT = True
CELERY_ACKS_LATE = True
CELERY_TASK_SERIALIZER = "pickle"
CELERY_RESULT_SERIALIZER = "pickle"
CELERY_ACCEPT_CONTENT = ['pickle']
CELERY_TIMEZONE = "Asia/Shanghai"
CELERY_RESULT_BACKEND = "amqp"
CELERY_EVENT_QUEUE_TTL = 10
CELERY_EVENT_QUEUE_EXPIRES = 10
CELERY_SEND_EVENTS = False


CELERY_QUEUES = {
    "sync_customer_list": {
        "routing_key": "sync.customer.list",
        "exchange": "sync_customer_list",
        "exchange_type": "direct",
    },
    "sync_smt_customer_list": {
        "routing_key": "sync.smt.customer.list",
        "exchange": "sync_smt_customer_list",
        "exchange_type": "direct",
    },
    "sync_customer_detail": {
        "routing_key": "sync.customer.detail",
        "exchange": "sync_customer_detail",
        "exchange_type": "direct",
    },
    "sync_smt_customer_detail": {
        "routing_key": "sync.smt.customer.detail",
        "exchange": "sync_smt_customer_detail",
        "exchange_type": "direct",
    },
}

CELERY_ROUTES = (
    {
        "morph.task.sync_customer_list.sync_customer_list": {
            "routing_key": "sync.customer.list",
            "queue": "sync_customer_list",
        }
    },
    {
        "morph.task.sync_customer_list.sync_smt_customer_list": {
            "routing_key": "sync.smt.customer.list",
            "queue": "sync_smt_customer_list",
        }
    },
    {
        "morph.task.sync_customer_detail.sync_customer_detail": {
            "routing_key": "sync.customer.detail",
            "queue": "sync_customer_detail",
        }
    },
    {
        "morph.task.sync_customer_detail.sync_smt_customer_detail": {
            "routing_key": "sync.smt.customer.detail",
            "queue": "sync_smt_customer_detail",
        }
    },
)

CELERY_IMPORTS = (
    "morph.task.sync_customer_list",
    "morph.task.sync_customer_detail",
)

CELERY_SEND_TASK_ERROR_EMAILS = False

BROKER_URL = 'amqp://kratos:GZLxVSdOQTIIKGpeoC3vv5Myh@154.actneed.com:5672/morph'