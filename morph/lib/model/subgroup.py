# -*- coding: utf-8 -*-

# @author: xuhe
# @date: 15/7/2
# @description: 


import sqlalchemy as SA
from morph.lib.model.base import Base
from sqlalchemy.dialects.mysql import BIGINT


class SubGroup(Base):
    __tablename__ = "subgroup"

    id = SA.Column(SA.INTEGER, primary_key=True, autoincrement=True)
    shop_id = SA.Column(BIGINT(unsigned=True), SA.ForeignKey("shop.id"), nullable=False)
    category_id = SA.Column(BIGINT(unsigned=True), SA.ForeignKey("category.id"), nullable=False)

    @classmethod
    def create(cls, session, shop_id, category_id):
        if cls.is_group_exists(session, shop_id, category_id):
            return 0
        subgroup = cls(shop_id=shop_id, category_id=category_id)
        session.add(subgroup)
        session.commit()

    @classmethod
    def find_by_id(cls, session, subgroup_id):
        return session.query(cls).filter(cls.id == subgroup_id).first()

    @classmethod
    def is_group_exists(cls, session, shop_id, category_id):
        subgroup = session.query(cls).filter(
            SA.and_(
                cls.shop_id == shop_id,
                cls.category_id == category_id
            )
        ).first()
        return True if subgroup else False

    @classmethod
    def del_record(cls, session, shop_id, category_id):
        subgroup = session.query(cls).filter(
            SA.and_(
                cls.shop_id == shop_id,
                cls.category_id == category_id
            )
        ).first()
        session.delete(subgroup)
        session.commit()

    def to_json(self):
        return {
            "id": self.id,
            "category_id": self.category_id,
            "shop_id": self.shop_id
        }