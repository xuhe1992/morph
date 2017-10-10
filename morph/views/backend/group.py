# coding=utf8

from morph.views.base import BaseHandler
from morph.lib.utils.logger_util import logger
from morph.lib.model.session import sessionCM
from morph.lib.model.group import Group


class GroupHandler(BaseHandler):

    def get(self, *args, **kwargs):
        logger.info(self.params)

        method_route = {
            "group/update": self.update_group,
            "group/delete": self.delete_group,
            "group/list": self.select_group
        }

        action = args[0]

        self.write(method_route[action]())

    def post(self, *args, **kwargs):
        logger.info(self.params)
        method_route = {
            "group/save": self.save_group,
        }

        action = args[0]

        self.write(method_route[action]())
        self.write(self.params)

    def save_group(self):
        logger.info(self.params)
        user_id = self.current_user.id
        name = self.params.get("name", "")
        kw = dict()

        if not name:
            return {"status": 0, "data": "参数：\"name\"缺失！"}

        kw["user_id"] = user_id
        kw["name"] = name

        with sessionCM() as session:
            group = Group.create(session, **kw)
        if group:
            return {"status": 1, "data": "创建成功！"}
        else:
            return {"status": 0, "data": "创建失败！"}

    def update_group(self):
        logger.info(self.params)
        kw = {}

        group_id = self.params.get("group_id", "")
        if not group_id:
            return {"status": 0, "data": "必填参数\"group_id\"缺失！"}

        if self.params.get("name", ""):
            kw["name"] = self.params.get("name", "")

        with sessionCM() as session:
            group = Group.find_by_id(session, group_id=group_id)
            if not group:
                return {"status": 0, "data": "template不存在！"}
            Group.update(session, group, **kw)

        return {"status": 1, "data": "更新成功！"}

    def delete_group(self):
        logger.info(self.params)
        user_id = self.params.get("user", "")
        if user_id:
            user_id = self.current_user.id
        else:
            user_id = False
        group_ids = self.params.get("group_id", "").split(";")

        with sessionCM() as session:
            if group_ids:
                for group_id in group_ids:
                    Group.remove(session, group_id=group_id)
                return {"status": 1}

            if user_id:
                Group.bulk_remove(session, user_id=user_id)
                return {"status": 1}

            return {"status": 0}

    def select_group(self):
        logger.info(self.params)
        group_id = self.params.get("group_id", "")
        user_id = self.params.get("user", "")
        if user_id:
            user_id = self.current_user.id
        else:
            user_id = False

        result, tmp = [], []
        with sessionCM() as session:
            if group_id:
                result = Group.find_by_id(session, group_id)

            if user_id:
                result = Group.find_by_user_id(session, user_id)
        if not isinstance(result, list):
            result = [result]
        for item in result:
            tmp.append({
                "id": item.id,
                "user_id": item.user_id,
                "name": item.name,
            })

        return {
            "status": 1,
            "data": tmp
        }
