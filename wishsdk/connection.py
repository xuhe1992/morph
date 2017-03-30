# -*- coding:utf-8 -*-

__author__ = 'GF'


import json
import requests
import traceback
from config import Config
from urllib import urlencode
from furion.config import settings
from furion.lib.utils.logger_util import logger


class Connection(object):

    GET_VERBS = [
        "ticket", "ticket/get-action-required", "product", "variant", "product/multi-get",
        "order", "order/multi-get", "order/get-fulfill", "variant/multi-get"
    ]

    def __init__(self):
        self.domain = "merchant.wish.com"
        self.url_prefix = "https://merchant.wish.com/api/v2"
        self.async_mode = False
        self.config = Config(
            domain=self.domain,
            config_file=settings.wish_yaml
        )
        self.base_verbs = ""
        self.verb = ""
        self.shop_id = ""
        self.account = ""
        self.session = ""

    def check_verb(self, verb):
        self.verb = verb
        logger.info("WishSDK正在执行%s请求" % self.verb)
        logger.info(self.verb)
        if self.verb not in self.base_verbs:
            logger.info("invalid request name")
            return {
                "success": False,
                "error_code": "AC-WISH-10001",
                "error_message": "您提交的请求中含有不属于该请求的verb"
            }
        else:
            return {"success": True}

    def generate_request_url(self):
        return "%s/%s" % (
            self.url_prefix,
            self.verb,
        )

    def execute(self, verb, params):
        logger.info("++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++")
        check_result = self.check_verb(verb)
        if not check_result["success"]:
            return check_result
        try_times = 0
        while try_times < 3:
            try_times += 1
            try:
                if try_times > 1:
                    logger.info("...正在重新请求...")
                url = self.generate_request_url()
                logger.info(u"请求参数为%s" % params)
                if verb in self.GET_VERBS:
                    url = "?".join([url, urlencode(params)])
                    res = requests.get(url, timeout=30)
                else:
                    res = requests.post(url, params, timeout=30)
                logger.info(u"获取到的数据结果为%s" % res.text[0:2000])
                response_dict = json.loads(res.text)
                response_dict["success"] = not response_dict.get("code")
                logger.info("WishSDK请求执行完毕")
                logger.info("+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++")
                return response_dict
            except Exception, e:
                logger.info(traceback.format_exc(e))

        logger.info("+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++")
        return {
            "success": False,
            "error_code": "AC-WISH-10003",
            "exception": "请求超时，请稍后重试"
        }

    def start_auth(self):
        url = "https://%s/oauth/authorize" % self.domain
        params = dict(
            client_id=self.config.get("client_id")
        )
        return "?".join([url, urlencode(params)])

    def get_token(self, code):
        logger.info("WishSDK正在执行获取token的操作")
        try_times = 3
        while try_times > 0:
            res = None
            try:
                url = "https://%s/api/v2/oauth/access_token" % self.domain
                logger.info(u"请求链接为：%s" % url)
                params = dict(
                    grant_type="authorization_code",
                    client_id=self.config.get("client_id"),
                    client_secret=self.config.get("client_secret"),
                    redirect_uri=self.config.get("redirect_uri"),
                    code=code
                )
                logger.info(u'请求参数：%s' % params)
                res = requests.post(url, params, timeout=20)
                logger.info(u'获取到的数据结果为%s' % res.text)
                logger.info("WishSDK请求执行完毕")
                return res.json()
            except Exception, e:
                try_times -= 1
                if try_times <= 0:
                    logger.error({
                        "response": res.text if res else "授权请求3次均超时",
                        "message": traceback.format_exc(e)
                    })

    def get_new_token(self, refresh_token):
        logger.info("WishSDK正在执行刷新token的操作")
        url = "https://%s/api/v2/oauth/refresh_token" % self.domain
        logger.info(u"请求链接为：%s" % url)
        params = dict(
            grant_type="refresh_token",
            client_id=self.config.get("client_id"),
            client_secret=self.config.get("client_secret"),
            refresh_token=refresh_token,
        )
        logger.info(u'请求参数：%s' % params)
        res = requests.post(url, params, timeout=20)
        logger.info(u'获取到的数据结果为%s' % res.text)
        logger.info("WishSDK请求执行完毕")
        return res.json()
