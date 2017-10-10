# -*- coding: utf-8 -*-
import sqlalchemy as sa
from sqlalchemy.dialects.mysql import BIGINT
from sqlalchemy.orm.exc import NoResultFound, MultipleResultsFound
from morph.lib.model.base import Base


class Configuration(Base):
    """
    智能客服配置数据
    """
    __tablename__ = "configuration"

    id = sa.Column(BIGINT(unsigned=True), primary_key=True, autoincrement=True)
    shop_id = sa.Column(BIGINT(unsigned=True), nullable=False)
    content = sa.Column(sa.String(2048), nullable=True)
    status = sa.Column(sa.SMALLINT, nullable=False)
    count = sa.Column(sa.INT)
    condition = sa.Column(sa.String(45), nullable=True)
    type = sa.Column(sa.String(45), nullable=False)

    @classmethod
    def create(cls, session, **kwargs):
        configuration = cls()
        for key, value in kwargs.items():
            setattr(configuration, key, value)
        session.add(configuration)
        session.commit()
        return configuration

    @classmethod
    def update(cls, session, configuration, upsert=True, **kwargs):
        if not configuration and not upsert:
            return False
        configuration = configuration or cls()
        for key, value in kwargs.items():
            setattr(configuration, key, value)
        session.add(configuration)
        session.commit()
        return configuration

    @classmethod
    def remove(cls, session, configuration_id=None, configuration=None):
        if not configuration and not configuration_id:
            return False
        if not configuration:
            configuration = cls.find_by_id(session, configuration_id)
        session.delete(configuration)
        session.commit()
    
    @classmethod
    def find_by_id(cls, session, configuration_id):
        try:
            return session.query(cls).filter(cls.id == configuration_id).one()
        except NoResultFound:
            pass
        except MultipleResultsFound:
            pass

    @classmethod
    def find_by_shop_id(cls, session, shop_id):
        try:
            return session.query(cls).filter(cls.shop_id == shop_id).all()
        except NoResultFound:
            pass
        except MultipleResultsFound:
            pass


