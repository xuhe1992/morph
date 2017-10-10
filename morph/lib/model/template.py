# -*- coding: utf-8 -*-
import sqlalchemy as sa
from sqlalchemy.dialects.mysql import BIGINT
from sqlalchemy.orm.exc import NoResultFound, MultipleResultsFound
from morph.lib.model.base import Base


class Template(Base):
    """
    模板数据
    """
    __tablename__ = "template"

    id = sa.Column(BIGINT(unsigned=True), primary_key=True, autoincrement=True)
    title = sa.Column(sa.String(128), nullable=False)
    content = sa.Column(sa.String(2048), nullable=False)
    user_id = sa.Column(BIGINT(unsigned=True), sa.ForeignKey("user.id"), nullable=False)
    type = sa.Column(sa.String(45), nullable=False)
    condition = sa.Column(sa.String(45))

    @classmethod
    def create(cls, session, **kwargs):
        template = cls()
        for key, value in kwargs.items():
            setattr(template, key, value)
        session.add(template)
        session.commit()
        return template

    @classmethod
    def update(cls, session, template, upsert=True, **kwargs):
        if not template and not upsert:
            return False
        template = template or cls()
        for key, value in kwargs.items():
            setattr(template, key, value)
        session.add(template)
        session.commit()
        return template

    @classmethod
    def remove(cls, session, template_id=None, template=None):
        if not template and not template_id:
            return False
        if not template:
            template = cls.find_by_id(session, template_id)
        session.delete(template)
        session.commit()

    @classmethod
    def bulk_remove(cls, session, user_id):
        if not user_id:
            return False
        session.query(cls).filter(cls.user_id == user_id).delete()
    
    @classmethod
    def find_by_id(cls, session, template_id):
        try:
            return session.query(cls).filter(cls.id == template_id).one()
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
