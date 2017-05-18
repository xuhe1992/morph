# -*- coding=utf-8 -*-

"""
@author:lance
@date:
@version:
@description:
"""

import sqlalchemy as SA
from sqlalchemy.dialects.mysql import BIGINT, INTEGER
from furion.lib.model.base import Base


class Management(Base):

    __tablename__ = "management"

    id = SA.Column(BIGINT(unsigned=True), primary_key=True, autoincrement=True)
    user_id = SA.Column(BIGINT(unsigned=True), SA.ForeignKey("user.id"), nullable=False)
    shop_id = SA.Column(BIGINT(unsigned=True), SA.ForeignKey("shop.id"), nullable=False)
    authority = SA.Column(INTEGER, nullable=False)
    master = SA.Column(INTEGER, nullable=False)

    @classmethod
    def create(cls, session, user_id, shop_id, authority, master):
        if not cls.find_management(session, user_id, shop_id):
            management = cls(user_id=user_id, shop_id=shop_id, authority=authority, master=master)
            session.add(management)
            session.commit()

    @classmethod
    def find_management(cls, session, user_id, shop_id):
        management = session.query(cls).filter(
            SA.and_(cls.user_id == user_id,
                    cls.shop_id == shop_id)
        ).first()
        return management

    @classmethod
    def find_management_by_user_id(cls, session, user_id):
        managements = session.query(cls).filter(cls.user_id == user_id).all()
        return managements

    @classmethod
    def find_by_user_authority(cls, session, user_id, authority):
        managements = session.query(cls).filter(
            SA.and_(cls.user_id == user_id,
                    cls.authority == authority)
        ).all()

        return managements if managements else list()

    @classmethod
    def is_accessible(cls, session, user_id, shop_id):
        managements = session.query(cls).filter(
            SA.and_(cls.user_id == user_id,
                    cls.shop_id == shop_id)
        ).first()
        if managements:
            return True
        else:
            return False

    @classmethod
    def find_by_shop_id(cls, session, shop_id):
        return session.query(cls).filter(cls.shop_id == shop_id).all()

    @classmethod
    def find_shop_member(cls, session, shop_id):
        managements = session.query(cls).filter(cls.shop_id == shop_id).all()
        return [management.user_id for management in managements]

    @classmethod
    def delete(cls, session, user_id, shop_id):
        management = session.query(cls).filter(
            SA.and_(cls.user_id == user_id,
                    cls.shop_id == shop_id)
        ).first()
        session.delete(management)
        session.commit()

    @classmethod
    def is_master(cls, session, user_id, shop_id):
        management = session.query(cls).filter(
            SA.and_(cls.user_id == user_id,
                    cls.shop_id == shop_id)
        ).first()
        if management.master == 1:
            return True
        else:
            return False

    @classmethod
    def find_child_user(cls, session, shop_id):
        managements = session.query(cls).filter(
            SA.and_(cls.shop_id == shop_id,
                    cls.master != 1)
        ).all()
        return managements

    @classmethod
    def find_create_user_id(cls, session, shop_id):
        management = session.query(cls).filter(
            SA.and_(cls.shop_id == shop_id,
                    cls.master == 1)
        ).first()
        if management:
            return management.user_id
        else:
            return None

    @classmethod
    def find_user_shop(cls, session, user_id):
        managements = session.query(cls.shop_id).filter(cls.user_id == user_id).all()
        return [management.shop_id for management in managements]

