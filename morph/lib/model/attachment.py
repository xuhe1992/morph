# -*- coding: utf-8 -*-

"""
@author: xuhe
@date: 17/5/16
@description: 
"""

import sqlalchemy as sa
from sqlalchemy.dialects.mysql import BIGINT
from sqlalchemy.orm.exc import NoResultFound, MultipleResultsFound
from morph.lib.model.base import Base


class Attachment(Base):
    """
    客服附加消息，产品图片、链接、标题
    """
    __tablename__ = "attachment"

    id = sa.Column(BIGINT(unsigned=True), primary_key=True, autoincrement=True)
    channel_id = sa.Column(BIGINT(unsigned=True), sa.ForeignKey("channel.id"), nullable=False)
    name = sa.Column(sa.String(256), nullable=False)
    image_url = sa.Column(sa.String(256), nullable=False)
    product_id = sa.Column(sa.String(16), nullable=False)
    product_url = sa.Column(sa.String(256), nullable=False)
    order_id = sa.Column(sa.String(16), nullable=False)
    order_url = sa.Column(sa.String(256), nullable=False)
    
    @classmethod
    def create(cls, session, **kwargs):
        attachment = cls()
        for key, value in kwargs.items():
            setattr(attachment, key, value)
        session.add(attachment)
        session.commit()
        return attachment

    @classmethod
    def update(cls, session, attachment, upsert=True, **kwargs):
        if not attachment and not upsert:
            return False
        attachment = attachment or cls()
        for key, value in kwargs.items():
            setattr(attachment, key, value)
        session.add(attachment)
        session.commit()
        return attachment

    @classmethod
    def remove(cls, session, attachment_id=None, attachment=None):
        if not attachment and not attachment_id:
            return False
        if not attachment:
            attachment = cls.find_by_id(session, attachment_id)
        session.delete(attachment)
        session.commit()
        
    @classmethod
    def find_by_id(cls, session, attachment_id):
        try:
            return session.query(cls).filter(cls.id == attachment_id).one()
        except NoResultFound:
            pass
        except MultipleResultsFound:
            pass
