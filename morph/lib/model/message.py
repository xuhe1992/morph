# -*- coding: utf-8 -*-

"""
@author: xuhe
@date: 17/3/30
@description: 
"""

import sqlalchemy as sa
from sqlalchemy.dialects.mysql import BIGINT
from sqlalchemy.orm.exc import NoResultFound, MultipleResultsFound
from morph.lib.model.base import Base


class Message(Base):
    """
    通讯管道表
    """
    __tablename__ = "message"

    id = sa.Column(BIGINT(unsigned=True), primary_key=True, autoincrement=True)
    channel_id = sa.Column(BIGINT(unsigned=True), nullable=False)
    origin_id = sa.Column(sa.String(64), nullable=False)
    msg_type = sa.Column(sa.String(32), nullable=True)
    content = sa.Column(sa.Text, nullable=False)
    image_urls = sa.Column(sa.String(1024), nullable=True)
    receive_time = sa.Column(sa.Date, nullable=False)
    
    @classmethod
    def create(cls, session, **kwargs):
        message = cls()
        for key, value in kwargs.items():
            setattr(message, key, value)
        session.add(message)
        session.commit()
        return message

    @classmethod
    def update(cls, session, message, upsert=True, **kwargs):
        if not message and not upsert:
            return False
        message = message or cls()
        for key, value in kwargs.items():
            setattr(message, key, value)
        session.add(message)
        session.commit()
        return message

    @classmethod
    def remove(cls, session, message_id=None, message=None):
        if not message and not message_id:
            return False
        if not message:
            message = cls.find_by_id(session, message_id)
        session.delete(message)
        session.commit()
    
    @classmethod
    def find_by_id(cls, session, message_id):
        try:
            return session.query(cls).filter(cls.id == message_id).one()
        except NoResultFound:
            pass
        except MultipleResultsFound:
            pass