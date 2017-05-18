# -*- coding: utf-8 -*-

# @author: xuhe
# @date: 15/3/17
# @description: 


import sqlalchemy as SA
from sqlalchemy.dialects.mysql import BIGINT, INTEGER
from sqlalchemy.orm.exc import MultipleResultsFound, NoResultFound
from morph.lib.model.base import Base


class Task(Base):

    __tablename__ = "task"

    id = SA.Column(BIGINT(unsigned=True), primary_key=True, autoincrement=True)
    mold = SA.Column(SA.String(32), nullable=False)
    shop_id = SA.Column(BIGINT(unsigned=True), nullable=True)
    user_id = SA.Column(BIGINT(unsigned=True), nullable=True)
    remark = SA.Column(SA.String(1024), nullable=True)
    status = SA.Column(INTEGER, nullable=False, default=0)

    @classmethod
    def create(cls, session, mold, shop_id, user_id, remark="0;0"):
        task = Task(mold=mold, shop_id=shop_id, user_id=user_id, remark=remark)
        session.add(task)
        session.commit()
        return task.id

    @classmethod
    def save(cls, session, task):
        session.add(task)
        session.commit()
        return task.id

    @classmethod
    def update(cls, session, task):
        session.add(task)
        session.commit()

    @classmethod
    def find_by_id(cls, session, task_id):
        try:
            task = session.query(Task).filter(Task.id == task_id).one()
        except MultipleResultsFound:
            return None
        except NoResultFound:
            return None
        return task

    @classmethod
    def find_by_shop_mold(cls, session, shop_id, mold):
        try:
            task = session.query(Task).filter(
                SA.and_(Task.shop_id == shop_id, Task.mold == mold)
            ).one()
        except MultipleResultsFound:
            return None
        except NoResultFound:
            return None
        return task

    @classmethod
    def find_by_user_mold(cls, session, user_id, mold):
        try:
            task = session.query(Task).filter(
                SA.and_(Task.user_id == user_id, Task.mold == mold)
            ).one()
        except MultipleResultsFound:
            return None
        except NoResultFound:
            return None
        return task

    @classmethod
    def find_multi_by_user_mold(cls, session, user_id, mold):
        return session.query(Task).filter(
            SA.and_(Task.user_id == user_id, Task.mold == mold)
        ).all()

    def to_json(self):
        return {
            "id": self.id,
            "mold": self.mold,
            "shop_id": self.shop_id,
            "user_id": self.user_id,
            "remark": self.remark,
            "status": self.status
        }

    @classmethod
    def to_object(cls, shop):
        return cls(
            id=shop["id"],
            name=shop["name"],
            platform=shop["platform"],
            owner=shop["owner"],
            session=shop["session"],
            account=shop["account"],
            site_id=shop["site_id"]
        )