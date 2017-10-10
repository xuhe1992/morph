# coding=utf8

from morph.views.base import BaseHandler
from morph.lib.utils.logger_util import logger
from morph.lib.model.session import sessionCM
from morph.lib.model.contacts import Contacts


class ContactsHandler(BaseHandler):

    def get(self, *args, **kwargs):
        logger.info(self.params)

        method_route = {
            "contacts/update": self.update_contacts,
            "contacts/delete": self.delete_contacts,
            "contacts/list": self.select_contacts
        }

        action = args[0]

        self.write(method_route[action]())

    def post(self, *args, **kwargs):
        logger.info(self.params)
        method_route = {
            "contacts/save": self.save_contacts,
        }

        action = args[0]

        self.write(method_route[action]())
        self.write(self.params)

    def save_contacts(self):
        logger.info(self.params)
        user_id = self.current_user.id  # self.params.get("user_id", "")
        name = self.params.get("name", "")
        origin_id = self.params.get("origin_id")
        group_id = self.params.get("group_id")
        m_type = self.params.get("type", "normal")  # 可选值 normal, black, white
        platform = self.params.get("platform" "")
        kw = dict()

        if not origin_id:
            return {"status": 0, "message": "参数：\"origin_id\"缺失！"}
        if not platform:
            return {"status": 0, "message": "参数：\"platform\"缺失！"}

        kw["user_id"] = user_id
        kw["name"] = name or ""
        kw["origin_id"] = origin_id
        kw["group_id"] = group_id or ""
        kw["type"] = m_type or ""
        kw["platform"] = platform

        with sessionCM() as session:
            contacts = Contacts.create(session, **kw)
        if contacts:
            return {"status": 1, "message": "创建成功！"}
        else:
            return {"status": 0, "message": "创建失败！"}

    def update_contacts(self):
        logger.info(self.params)
        kw = {}

        contacts_id = self.params.get("contacts_id", "")
        if not contacts_id:
            return {"status": 0, "message": "必填参数\"contacts_id\"缺失！"}

        if self.params.get("name", ""):
            kw["name"] = self.params.get("name", "")

        if self.params.get("origin_id", ""):
            kw["origin_id"] = self.params.get("origin_id", "")

        if self.params.get("group_id", ""):
            kw["group_id"] = self.params.get("group_id", "")

        if self.params.get("type", ""):
            kw["type"] = self.params.get("type", "")

        with sessionCM() as session:
            contacts = Contacts.find_by_id(session, contacts_id=contacts_id)
            if not contacts:
                return {"status": 0, "message": "contacts不存在！"}

            contacts.update(session, contacts, **kw)

        return {"status": 1, "message": "更新成功！"}

    def delete_contacts(self):
        logger.info(self.params)
        # user_id = # self.params.get("user_id", "")
        contacts_ids = self.params.get("contacts_id", "").split(";")

        with sessionCM() as session:
            if contacts_ids:
                for contacts_id in contacts_ids:
                    Contacts.remove(session, contacts_id=contacts_id)
                return {"status": 1, "message": "删除成功！"}

            # if user_id:
            #     contacts.bulk_remove(session, user_id=user_id)
            #     return {"status": 1}

            return {"status": 0, "message": "删除失败！"}

    def select_contacts(self):
        logger.info(self.params)
        contacts_id = self.params.get("contacts_id", "")
        m_type = self.params.get("type")
        group_id = self.params.get("group_id", "")
        platform = self.params.get("platform", "")

        result, tmp = [], []
        with sessionCM() as session:
            if contacts_id:
                result = Contacts.find_by_id(session, contacts_id)
            else:
                result = Contacts.find_by_user_id(session, self.current_user.id)
                result = [item for item in result if item.platform == platform] if platform else result
                result = [item for item in result if item.type == m_type] if m_type else result
                result = [item for item in result if item.group_id == group_id] if group_id else result
        if not isinstance(result, list):
            result = [result]
        for item in result:
            tmp.append({
                "id": item.id,
                "user_id": item.user_id,
                "name": item.name,
                "origin_id": item.origin_id,
                "group_id": item.group_id,
                "type": item.type
            })

        return {
            "status": 1,
            "data": tmp,
            "message": ""
        }

    def import_from_csv(self):
        """
        从csv中读取联系人信息

        :return:
        """
        logger.info(self.params)
        pass

