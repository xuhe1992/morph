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
    消息数据，一个管道包含多条消息数据
    """
    __tablename__ = "message"

    id = sa.Column(BIGINT(unsigned=True), primary_key=True, autoincrement=True)
    channel_id = sa.Column(BIGINT(unsigned=True), sa.ForeignKey("channel.id"), nullable=False)
    origin_id = sa.Column(sa.String(64), nullable=False)
    content = sa.Column(sa.Text(collation="utf8_bin"), nullable=False)
    image_urls = sa.Column(sa.String(1024), nullable=True)
    receive_time = sa.Column(sa.DateTime, nullable=False)
    source = sa.Column(sa.String(8), nullable=False)
    
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

    @classmethod
    def find_by_origin_id(cls, session, origin_id):
        try:
            return session.query(cls).filter(cls.origin_id == origin_id).one()
        except NoResultFound:
            pass
        except MultipleResultsFound:
            pass