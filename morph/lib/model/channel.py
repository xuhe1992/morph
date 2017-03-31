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


class Channel(Base):
    """
    通讯管道表
    """
    __tablename__ = "channel"

    id = sa.Column(BIGINT(unsigned=True), primary_key=True, autoincrement=True)
    seller_id = sa.Column(sa.String(128), nullable=False)
    seller_name = sa.Column(sa.String(128), nullable=False)
    buyer_id = sa.Column(sa.String(128), nullable=False)
    buyer_name = sa.Column(sa.String(128), nullable=True)
    read_stat = sa.Column(sa.SmallInteger, nullable=False)
    deal_stat = sa.Column(sa.SmallInteger, nullable=False)
    open_date = sa.Column(sa.Date, nullable=False)
    close_date = sa.Column(sa.Date, nullable=True)
    closed_by = sa.Column(sa.String(128), nullable=True)
    flag = sa.Column(sa.String(16), nullable=True)
    # 平台上的管道ID
    origin_id = sa.Column(sa.String(32), nullable=False)
    # 与管道相关联的产品、订单的ID
    relation_id = sa.Column(sa.String(32), nullable=True)
    # 与管道相关联的产品、订单等类型
    relation_type = sa.Column(sa.String(32), nullable=True)
    last_msg_date = sa.Column(sa.Date, nullable=False)
    last_msg_id = sa.Column(sa.String(32), nullable=False)
    last_msg_content = sa.Column(sa.String(64), nullable=False)

    @classmethod
    def create(cls, session, **kwargs):
        channel = cls()
        for key, value in kwargs.items():
            setattr(channel, key, value)
        session.add(channel)
        session.commit()
        return channel

    @classmethod
    def update(cls, session, channel, upsert=True, **kwargs):
        if not channel and not upsert:
            return False
        channel = channel or cls()
        for key, value in kwargs.items():
            setattr(channel, key, value)
        session.add(channel)
        session.commit()
        return channel

    @classmethod
    def remove(cls, session, channel_id=None, channel=None):
        if not channel and not channel_id:
            return False
        if not channel:
            channel = cls.find_by_id(session, channel_id)
        session.delete(channel)
        session.commit()

    @classmethod
    def find_by_id(cls, session, channel_id):
        try:
            return session.query(cls).filter(cls.id == channel_id).one()
        except NoResultFound:
            pass
        except MultipleResultsFound:
            pass