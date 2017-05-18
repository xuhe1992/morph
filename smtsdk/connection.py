# -*- coding: utf-8 -*-

# @author: xuhe
# @date: 15/1/23
# @description: base class to connect ali-express api

import json
import requests
import traceback
from urllib import urlencode
from smtsdk.config import Config
from smtsdk.utils import api_signature_rule, param_signature_rule
from morph.config import settings
from morph.lib.utils.logger_util import logger


class Connection(object):

    def __init__(self):

        self.domain = "gw.api.alibaba.com"
        self.url_prefix = "https://gw.api.alibaba.com/openapi"
        self.async_mode = False
        self.config = Config(
            domain=self.domain,
            config_file=settings.ali_yaml
        )
        self.version = self.config.get("version")
        self.namespace = self.config.get("namespace")
        self.protocol = self.config.get("protocol")
        self.need_signature = True
        self.base_verbs = ""
        self.verb = ""
        self.shop_id = ""
        self.account = ""
        self.session = ""

    def check_verb(self, verb):
        self.verb = verb
        logger.info("AliSDK正在执行%s请求" % self.verb)
        logger.info(self.verb)
        if self.verb not in self.base_verbs:
            logger.info("invalid request name")
            return {
                "success": False,
                "error_code": "AC-SMT-10001",
                "error_message": "您提交的请求中含有不属于该请求的verb"
            }
        else:
            return {"success": True}

    def prepare(self, params):
        logger.info(u"请求参数为%s" % params)

        url = self.generate_request_url()
        logger.info(u"请求链接为%s" % url)
        path = self.generate_path()
        signature = api_signature_rule(
            self.config.get("secret_key"),
            path,
            params
        )
        params.update(_aop_signature=signature)
        return url, params

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
                url, params = self.prepare(params)
                logger.info("参数准备完毕，开始请求，超时时间为20S")
                res = requests.post(url, params, timeout=20)
                logger.info(u"获取到的数据结果为%s" % res.text[0:2000])
                response_dict = json.loads(res.text)
                if response_dict.get("exception"):
                    response_dict.update(success=False)
                    return response_dict
                if response_dict.get("error"):
                    response_dict.update(success=False)
                    return response_dict
                if response_dict.get("success") is False:
                    response_dict.update(success=False)
                    return response_dict
                response_dict.update(success=True)
                logger.info("AliSDK请求执行完毕")
                logger.info("+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++")
                return response_dict
            except Exception, e:
                logger.info(traceback.format_exc(e))
                del params["_aop_signature"]

        logger.info("+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++")
        return {
            "success": False,
            "error_code": "AC-SMT-10003",
            "exception": "请求超时，请稍后重试"
        }

    def generate_request_url(self):
        return "%s/%s/%s/%s/%s/%d" % (
            self.url_prefix,
            self.protocol,
            self.version,
            self.namespace,
            self.verb,
            self.config.get("app_key")
        )

    def generate_path(self):
        return "%s/%s/%s/%s/%d" % (
            self.protocol,
            self.version,
            self.namespace,
            self.verb,
            self.config.get("app_key")
        )

    def start_auth(self, **kwargs):
        url = "http://gw.api.alibaba.com/auth/authorize.htm"
        params = dict(
            client_id=self.config.get("app_key"),
            site="aliexpress",
            redirect_uri=self.config.get("redirect_uri"),
        )
        if kwargs:
            params["state"] = urlencode(kwargs)

        signature = param_signature_rule(self.config.get("secret_key"), params)
        params.update(_aop_signature=signature)
        return "?".join([url, urlencode(params)])

    def get_token(self, code):
        logger.info("AliSDK正在执行获取token的操作")
        try_times = 3
        while try_times > 0:
            res = None
            try:
                url = "https://gw.api.alibaba.com/openapi/param2/1/system.oauth2/getToken/%s" % self.config.get("app_key")
                logger.info(u"请求链接为：%s" % url)
                params = dict(
                    grant_type="authorization_code",
                    need_refresh_token=True,
                    client_id=self.config.get("app_key"),
                    client_secret=self.config.get("secret_key"),
                    redirect_uri=self.config.get("redirect_uri"),
                    code=code
                )
                logger.info(u'请求参数：%s' % params)
                res = requests.post(url, params, timeout=20)
                logger.info(u'获取到的数据结果为%s' % res.text)
                logger.info("AliSDK请求执行完毕")
                return json.loads(res.text)
            except Exception, e:
                try_times -= 1
                if try_times <= 0:
                    logger.error({
                        "response": res.text if res else "授权请求3次均超时",
                        "message": traceback.format_exc(e)
                    })

    def get_new_token(self, refresh_token):
        logger.info("AliSDK正在执行刷新token的操作")
        url = "https://gw.api.alibaba.com/openapi/param2/1/system.oauth2/getToken/%s" % self.config.get("app_key")
        logger.info(u"请求链接为：%s" % url)
        params = dict(
            grant_type="refresh_token",
            client_id=self.config.get("app_key"),
            client_secret=self.config.get("secret_key"),
            refresh_token=refresh_token,
        )
        logger.info(u'请求参数：%s' % params)
        res = requests.post(url, params, timeout=20)
        logger.info(u'获取到的数据结果为%s' % res.text)
        logger.info("AliSDK请求执行完毕")
        return json.loads(res.text)


if __name__ == "__main__":
    print Connection().get_token(7084831)