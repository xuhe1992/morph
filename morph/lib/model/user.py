# -*- coding=utf-8 -*-

"""
@author:lance
@date:
@version:
@description:
"""

import sqlalchemy as sa
from sqlalchemy.dialects.mysql import BIGINT
from sqlalchemy.orm import relationship
from morph.lib.model.base import Base
from morph.lib.model.manage import Management


class User(Base):
    """
    用户表
    """
    __tablename__ = "user"

    MEMBER, ADMIN = 0, 1

    id = sa.Column(BIGINT(unsigned=True), primary_key=True, autoincrement=True)
    mobile = sa.Column(sa.String(32), nullable=False, unique=True, index=True)
    email = sa.Column(sa.String(64), nullable=True, unique=True, index=True)
    password = sa.Column(sa.String(128), nullable=False)
    name = sa.Column(sa.String(64), nullable=True)
    avatar = sa.Column(sa.String(256))
    authority = sa.Column(sa.SmallInteger, default=MEMBER)
    master = sa.Column(BIGINT(unsigned=True), nullable=True)
    func = sa.Column(sa.String(64), nullable=True)

    managements = relationship("Management", backref="user", cascade="delete, delete-orphan")

    def to_dict(self):
        return {
            "id": str(self.id),
            "email": self.email,
            "mobile": self.mobile,
            "name": self.name,
            "avatar": self.avatar
        }

    @classmethod
    def find_by_id(cls, session, user_id):
        user = session.query(User).filter(User.id == user_id).first()
        return user
