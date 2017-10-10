# coding=utf8

from sqlalchemy import and_
from morph.views.base import BaseHandler
from morph.lib.utils.logger_util import logger
from morph.lib.model.session import sessionCM
from morph.lib.model.configuration import Configuration
from morph.lib.model.shop import Shop


class ConfigurationHandler(BaseHandler):

    def get(self, *args, **kwargs):
        logger.info(self.params)

        method_route = {
            "configuration/update": self.update_configuration,
            "configuration/delete": self.delete_configuration,
            "configuration/list": self.select_configuration
        }

        action = args[0]

        self.write(method_route[action]())

    def post(self, *args, **kwargs):
        logger.info(self.params)
        method_route = {
            "configuration/save": self.save_configuration,
        }

        action = args[1]

        self.write(method_route[action]())
        self.write(self.params)

    def save_configuration(self):
        logger.info(self.params)
        shop_id = self.params.get("shop_id", "")
        content = self.params.get("content", "")
        status = self.params.get("status", 0)
        count = 0
        condition = self.params.get("condition")
        m_type = self.params.get("type")
        kw = dict()

        with sessionCM() as session:
            configuration = session.query(Configuration).filter(
                and_(
                    Configuration.shop_id == shop_id,
                    Configuration.type == type
                )
            ).one()
            if configuration:
                return {}

        if not shop_id:
            return {"status": 0, "data": "参数：\"shop_id\"缺失！"}
        if not content:
            return {"status": 0, "data": "\"参数：\"content\"缺失！"}
        if not condition:
            return {"status": 0, "data": "\"参数：\"condition\"缺失！"}

        kw["shop_id"] = shop_id
        kw["content"] = content
        kw["status"] = status
        kw["count"] = count
        kw["condition"] = condition
        kw["type"] = m_type

        with sessionCM() as session:
            configuration = Configuration.create(session, **kw)
        if configuration:
            return {"status": 1, "data": "创建成功！"}
        else:
            return {"status": 0, "data": "创建失败！"}

    def update_configuration(self):
        logger.info(self.params)
        kw = {}

        configuration_id = self.params.get("configuration_id", "")
        if not configuration_id:
            return {"status": 0, "data": "必填参数\"configuration_id\"缺失！"}

        if self.params.get("content", ""):
            kw["content"] = self.params.get("content", "")

        if self.params.get("status", ""):
            kw["status"] = self.params.get("status", "")

        if self.params.get("condition", ""):
            kw["condition"] = self.params.get("condition", "")

        if self.params.get("count", ""):
            kw["count"] = self.params.get("count", "")

        with sessionCM() as session:
            configuration = Configuration.find_by_id(session, configuration_id=configuration_id)
            if not configuration:
                return {"status": 0, "data": "configuration不存在！"}

            configuration.update(session, configuration, **kw)

        return {"status": 1, "data": "更新成功！"}

    def delete_configuration(self):
        logger.info(self.params)
        user_id = self.params.get("user_id", "")
        configuration_ids = self.params.get("configuration_id", "").split(";")

        with sessionCM() as session:
            if configuration_ids:
                for configuration_id in configuration_ids:
                    Configuration.remove(session, configuration_id=configuration_id)
                return {"status": 1, "message": "删除成功！"}

            return {"status": 0, "message": "删除失败！"}

    def select_configuration(self):
        logger.info(self.params)
        configuration_id = self.params.get("configuration_id", "")
        shop_ids = self.params.get("shop_ids", "").split(";")
        m_type = self.params.get("type", "")
        result, tmp = [], []

        with sessionCM() as session:
            if not configuration_id:
                for shop_id in shop_ids:
                    shop = Shop.find_by_id(session, shop_id)

                    if shop_id:
                        result = Configuration.find_by_shop_id(session, shop_id)
                        result = [item for item in result if item.type == m_type] if m_type else result

                    if not isinstance(result, list):
                        result = [result]
                    for item in result:
                        tmp.append({
                            "id": item.id,
                            "shop_id": item.shop_id,
                            "status": item.status,
                            "content": item.content,
                            "count": item.count,
                            "type": item.type,
                            "condition": item.condition,
                            "platform": shop.platform
                        })
            else:
                result = Configuration.find_by_id(session, configuration_id)
                shop = Shop.find_by_id(session, result.shop_id)
                for item in result:
                    tmp.append({
                        "id": item.id,
                        "shop_id": item.shop_id,
                        "status": item.status,
                        "content": item.content,
                        "count": item.count,
                        "type": item.type,
                        "condition": item.condition,
                        "platform": shop.platform
                    })

        return {
            "status": 1,
            "data": tmp
        }
