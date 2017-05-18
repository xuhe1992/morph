# -*- coding: utf-8 -*-

"""
@author: xuhe
@date: 17/1/16
@description: 
"""

import random
from string import digits, lowercase
from tornado.escape import to_unicode
from torndsession.sessionhandler import SessionBaseHandler
from hades.config import settings
from hades.lib.model.session import sessionCM
from hades.lib.model.user import User
from hades.lib.utils.logger_util import logger


class BaseHandler(SessionBaseHandler):

    def get(self, *args, **kwargs):
        self.on_request()

    def post(self, *args, **kwargs):
        self.on_request()

    @property
    def params(self):
        return self._argument()

    @property
    def cookies(self):
        return self._cookies()

    def prepare(self):
        if settings.offline:
            self.render(settings.offline_template)

    def _argument(self):
        return self._flatten_arguments(self.request.arguments)

    def _cookies(self):
        cookies = dict()
        cookie_str = self.request.headers.get("Cookie")
        for cookie in cookie_str.split(";"):
            name, value = cookie.strip().split("=", 1)
            cookies[name] = value
        return cookies

    def on_request(self):
        self.write_error(404)

    def get_current_user(self):
        try:
            user_id = self.session.get("user_id")
            with sessionCM() as session:
                user = session.query(User).filter(User.id == user_id).one()
                return user
        except Exception, e:
            logger.info(self.request.headers["X-Real-IP"])
            logger.info(e.message)

    def on_finish(self):
        self.session.flush()

    @staticmethod
    def str_to_unicode(word):
        try:
            return to_unicode(word)
        except Exception, e:
            logger.info(e.message)
            return word.decode("unicode-escape")

    def _flatten_arguments(self, args):
        """
        去除请求中单值参数的数组结构

        """
        flattened = {}
        for key in args:
            if len(args[key]) == 1:
                flattened[key] = self.str_to_unicode(args[key][0])
            else:
                flattened[key] = [self.str_to_unicode(arg) for arg in args[key]]

        return flattened

