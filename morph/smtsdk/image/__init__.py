# -*- coding: utf-8 -*-

# @author: xuhe
# @date: 15/4/7
# @description:


import json
import requests
from urllib import urlencode
from smtsdk.utils import api_signature_rule
from furion.lib.utils.logger_util import logger
from smtsdk.connection import Connection


class AliImage(Connection):

    def __init__(self, shop):
        Connection.__init__(self)
        self.base_verbs = [
            "api.uploadTempImage", "api.getPhotoBankInfo",
            "api.listImagePagination", "api.delUnUsePhoto"
        ]
        self.session = shop.session
        self.account = shop.account
        self.shop_id = shop.id

    def get_image_list(self, page=1, size=50):
        params = {
            "access_token": self.account,
            "locationType": "ALL_GROUP",
            "currentPage": page,
            "pageSize": size
        }
        self.need_signature = True
        response = self.execute("api.listImagePagination", params)
        return response

    def del_not_used_image(self, image_id):
        params = {
            "access_token": self.account,
            "imageRepositoryId": image_id
        }
        self.need_signature = True
        response = self.execute("api.delUnUsePhoto", params)
        return response

    def get_image_bank_info(self):
        params = {
            "access_token": self.account
        }
        self.need_signature = True
        response = self.execute("api.getPhotoBankInfo", params)
        return response

    def upload_temp_image(self, src_pic, src_file_name):
        content = self.get_image_content(src_pic)
        if not content:
            return ""
        logger.info("已请求到图片%s, 并开始上传" % src_pic)
        self.need_signature = True
        path = "param2/1/aliexpress.open/api.uploadTempImage/%d" % self.config.get("app_key")
        url = "http://gw.api.alibaba.com/fileapi/" + path
        params = {
            "access_token": str(self.account),
            "fileName": src_file_name
        }
        signature = api_signature_rule(self.config.get("secret_key"), path, params)
        params.update(_aop_signature=signature)
        url = "?".join([url, urlencode(params)])
        res = requests.post(url, data=content, timeout=15)

        logger.info("图片%s已完成上传，获得到的请求结果是:" % src_pic)
        logger.info(res.text)
        res_dict = json.loads(res.text)
        if res_dict.get("error_code") == "401":
            logger.warning("FUCK:上传图片又出现了401错误")
        if res_dict.get("status") == "NOCAPACITY":
            logger.warning("FUCK:上传图片又出现了NO CAPACITY错误")
        if res_dict.get("status") == "EXCEPTION":
            logger.warning("EXCEPTION:上传图片出现了错误")
        return res_dict.get("photobankUrl", "")

    def upload_image(self, pic_url, pic_name):
        content = self.get_image_content(pic_url)
        if not content:
            return ""
        logger.info("已请求到图片%s, 并开始上传" % pic_url)
        self.need_signature = True
        path = "param2/1/aliexpress.open/api.uploadImage/%d" % self.config.get("app_key")
        url = "http://gw.api.alibaba.com/fileapi/" + path
        params = {
            "access_token": str(self.account),
            "fileName": pic_name
        }
        signature = api_signature_rule(self.config.get("secret_key"), path, params)
        params.update(_aop_signature=signature)
        url = "?".join([url, urlencode(params)])
        res = requests.post(url, data=content, timeout=30)

        logger.info("图片%s已完成上传，获得到的请求结果是:" % pic_url)
        logger.info(res.text)
        res_dict = json.loads(res.text)
        if res_dict.get("error_code") == "401":
            logger.warning("FUCK:上传图片又出现了401错误")
        if res_dict.get("status") == "NOCAPACITY":
            logger.warning("FUCK:上传图片又出现了NO CAPACITY错误")
        if res_dict.get("status") == "EXCEPTION":
            logger.warning("EXCEPTION:上传图片出现了错误")
        return res_dict.get("photobankUrl", "")

    @classmethod
    def get_image_content(cls, pic_url):
        url = "http:" + pic_url if pic_url.startswith("//") else pic_url
        headers = {
            "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10_3) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/43.0.2357.132 Safari/537.36"
        }
        try_times = 2
        while try_times > 0:
            try:
                res = requests.get(url, headers=headers, timeout=15)
                if res.status_code != 200:
                    return False
                return res.content
            except Exception, e:
                logger.info(e.message)
                try_times -= 1
        return False