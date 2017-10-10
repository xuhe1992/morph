# -*- coding: utf-8 -*-
import sqlalchemy as sa
from sqlalchemy.dialects.mysql import BIGINT
from sqlalchemy.orm.exc import NoResultFound, MultipleResultsFound
from morph.lib.model.base import Base


class Group(Base):
    """
    分组数据
    """
    __tablename__ = "group"

    id = sa.Column(BIGINT(unsigned=True), primary_key=True, autoincrement=True)
    user_id = sa.Column(BIGINT(unsigned=True), nullable=False)
    name = sa.Column(sa.String(45), nullable=False)

    @classmethod
    def create(cls, session, **kwargs):
        group = cls()
        for key, value in kwargs.items():
            setattr(group, key, value)
        session.add(group)
        session.commit()
        return group

    @classmethod
    def update(cls, session, group, upsert=True, **kwargs):
        if not group and not upsert:
            return False
        group = group or cls()
        for key, value in kwargs.items():
            setattr(group, key, value)
        session.add(group)
        session.commit()
        return group

    @classmethod
    def remove(cls, session, group_id=None, group=None):
        if not group and not group_id:
            return False
        if not group:
            group = cls.find_by_id(session, group_id)
        session.delete(group)
        session.commit()

    @classmethod
    def bulk_remove(cls, session, user_id):
        if not user_id:
            return False
        session.query(cls).filter(cls.user_id == user_id).delete()
    
    @classmethod
    def find_by_id(cls, session, group_id):
        try:
            return session.query(cls).filter(cls.id == group_id).one()
        except NoResultFound:
            pass
        except MultipleResultsFound:
            pass

    @classmethod
    def find_by_user_id(cls, session, user_id):
        try:
            return session.query(cls).filter(cls.user_id == user_id).all()
        except NoResultFound:
            pass
        except MultipleResultsFound:
            pass
