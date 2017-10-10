# coding=utf8

from morph.views.base import BaseHandler
from morph.lib.utils.logger_util import logger
from morph.lib.model.session import sessionCM
from morph.lib.model.template import Template


class TemplateHandler(BaseHandler):

    def get(self, *args, **kwargs):
        logger.info(self.params)

        method_route = {
            "template/update": self.update_template,
            "template/delete": self.delete_template,
            "template/list": self.select_template
        }

        action = args[0]

        self.write(method_route[action]())

    def post(self, *args, **kwargs):
        logger.info(self.params)
        method_route = {
            "template/save": self.save_template,
        }

        action = args[0]

        self.write(method_route[action]())
        self.write(self.params)

    def save_template(self):
        logger.info(self.params)
        user_id = self.params.get("user_id", "")
        title = self.params.get("title", "")
        content = self.params.get("content")
        m_type = self.params.get("type")
        condition = self.params.get("condition")
        kw = dict()

        if not user_id:
            return {"status": 0, "data": "参数：\"user_id\"缺失！"}
        if not title:
            return {"status": 0, "data": "参数：\"title\"缺失！"}
        if not content:
            return {"status": 0, "data": "\"参数：\"content\"缺失！"}
        if not m_type:
            return {"status": 0, "data": "\"参数：\"type\"缺失！"}
        if not condition:
            return {"status": 0, "data": "\"参数：\"condition\"缺失！"}

        kw["user_id"] = user_id
        kw["title"] = title
        kw["content"] = content
        kw["type"] = m_type
        kw["condition"] = condition

        with sessionCM() as session:
            template = Template.create(session, **kw)
        if template:
            return {"status": 1, "data": "创建成功！"}
        else:
            return {"status": 0, "data": "创建失败！"}

    def update_template(self):
        logger.info(self.params)
        kw = {}

        template_id = self.params.get("template_id", "")
        if not template_id:
            return {"status": 0, "data": "必填参数\"template_id\"缺失！"}

        if self.params.get("title", ""):
            kw["title"] = self.params.get("title", "")

        if self.params.get("content", ""):
            kw["content"] = self.params.get("content", "")

        if self.params.get("condition", ""):
            kw["condition"] = self.params.get("condition", "")

        with sessionCM() as session:
            template = Template.find_by_id(session, template_id=template_id)
            if not template:
                return {"status": 0, "data": "template不存在！"}

            Template.update(session, template, **kw)

        return {"status": 1, "data": "更新成功！"}

    def delete_template(self):
        logger.info(self.params)
        user_id = self.params.get("user_id", "")
        template_ids = self.params.get("template_id", "").split(";")

        with sessionCM() as session:
            if template_ids:
                for template_id in template_ids:
                    Template.remove(session, template_id=template_id)
                return {"status": 1}

            if user_id:
                Template.bulk_remove(session, user_id=user_id)
                return {"status": 1}

            return {"status": 0}

    def select_template(self):
        logger.info(self.params)
        template_id = self.params.get("template_id", "")
        user_id = self.params.get("user_id", "")
        m_type = self.params.get("type", "")
        result, tmp = [], []
        with sessionCM() as session:
            if template_id:
                result = Template.find_by_id(session, template_id)

            if user_id:
                result = Template.find_by_user_id(session, user_id)
                result = [item for item in result if item.type == m_type] if m_type else result
        if not isinstance(result, list):
            result = [result]
        for item in result:
            tmp.append({
                "id": item.id,
                "user_id": item.user_id,
                "title": item.title,
                "content": item.content,
                "type": item.type,
                "condition": item.condition,
            })

        return {
            "status": 1,
            "data": tmp
        }
