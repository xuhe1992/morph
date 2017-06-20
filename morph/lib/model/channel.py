# -*- coding: utf-8 -*-

"""
@author: xuhe
@date: 17/3/30
@description: 
"""

import sqlalchemy as sa
from sqlalchemy.dialects.mysql import BIGINT
from sqlalchemy.orm import relationship
from sqlalchemy.orm.exc import NoResultFound, MultipleResultsFound
from morph.lib.model.base import Base
from morph.lib.model.attachment import Attachment
from morph.lib.model.message import Message


class Channel(Base):
    """
    通讯管道表
    """
    __tablename__ = "channel"

    id = sa.Column(BIGINT(unsigned=True), primary_key=True, autoincrement=True)
    shop_id = sa.Column(BIGINT(unsigned=True), nullable=False)
    seller_id = sa.Column(sa.String(128), nullable=False)
    seller_name = sa.Column(sa.String(128), nullable=False)
    buyer_id = sa.Column(sa.String(128), nullable=False)
    buyer_name = sa.Column(sa.String(128), nullable=True)
    read_stat = sa.Column(sa.SmallInteger, nullable=False)
    deal_stat = sa.Column(sa.SmallInteger, nullable=False)
    open_date = sa.Column(sa.DateTime, nullable=False)
    close_date = sa.Column(sa.DateTime, nullable=True)
    closed_by = sa.Column(sa.String(128), nullable=True)
    flag = sa.Column(sa.String(16), nullable=True)
    # 消息类型
    msg_source = sa.Column(sa.String(32), nullable=True)
    # 平台上的管道ID
    origin_id = sa.Column(sa.String(32), nullable=False)
    # 与管道相关联的产品、订单的ID，目前不确定是将SellerID作为一个通道的标志，还是将SellerID + RelationID作为标志，
    # 所以在Channel和Message中都添加了relation_id与relation_type
    relation_id = sa.Column(sa.String(32), nullable=True)
    # 与管道相关联的产品、订单等类型，目前不确定是将SellerID作为一个通道的标志，还是将SellerID + RelationID作为标志，
    # 所以在Channel和Message中都添加了relation_id与relation_type
    relation_type = sa.Column(sa.String(32), nullable=True)
    last_msg_date = sa.Column(sa.DateTime, nullable=True)
    last_msg_id = sa.Column(sa.String(32), nullable=True)
    last_msg_content = sa.Column(sa.String(64), nullable=True)

    attachment = relationship("Attachment", backref="channel", cascade="all, delete, delete-orphan")
    messages = relationship("Message", backref="channel", cascade="all, delete, delete-orphan")

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

    @classmethod
    def find_by_origin_id(cls, session, origin_id):
        try:
            return session.query(cls).filter(cls.origin_id == origin_id).one()
        except NoResultFound:
            pass
        except MultipleResultsFound:
            pass

    @classmethod
    def find_by_channel_composition(cls, session, seller_id, buyer_id, relation_id):
        try:
            return session.query(cls).filter(sa.and_(
                cls.seller_id == seller_id,
                cls.buyer_id == buyer_id,
                cls.relation_id == relation_id
            )).one()
        except NoResultFound:
            pass
        except MultipleResultsFound:
            pass