# -*- coding: utf-8 -*-

"""
@author: xuhe
@date: 17/1/16
@description: 
"""

from tornado.escape import to_unicode
from torndsession.sessionhandler import SessionBaseHandler
from morph.config import settings
from morph.lib.model.session import sessionCM
from morph.lib.model.user import User
from morph.lib.utils.logger_util import logger


class RequestUtilMixin(object):
    """
    对继承BaseHandler的对象进行扩展，使其拥有params属性，之所以不用以前的方式，是因为以前的方式每次调用self.params
    都会把全部逻辑（_flatten_arguments）执行一遍，现在的方法只会执行一遍并保留在_util_params_context中，以供下次
    调用，self.params中的值是可修改的，而不是每次获取都一样（之前的方式）。
    提示：在使用Mixin的时候，解释器最终会把多个继承的类（包括Mixin）融合在一起，这样的话，在Mixin中可以使用该对象集成的其他类的方法。
    比如在RequestUtilMixin中使用self.request.arguments也是可以的
    """

    @property
    def params(self):
        return self._create_util_mixin(self, "_util_params_context")

    def _create_util_mixin(self, context, inner_property_name):
        if not hasattr(self, inner_property_name):
            method_route = {
                "_util_params_context": self.get_params
            }
            setattr(self, inner_property_name, method_route[inner_property_name](context.request))
        return getattr(self, inner_property_name)

    def get_params(self, request):
        return self._flatten_arguments(request.arguments)

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

    @staticmethod
    def str_to_unicode(word):
        """
        将字符串转为unicode
        """
        try:
            return to_unicode(word)
        except Exception, e:
            logger.info(e.message)
            return word.decode("unicode-escape")


class BaseHandler(SessionBaseHandler, RequestUtilMixin):

    def get(self, *args, **kwargs):
        self.on_request()

    def post(self, *args, **kwargs):
        self.on_request()

    def prepare(self):
        if settings.offline:
            self.render(settings.offline_template)

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
