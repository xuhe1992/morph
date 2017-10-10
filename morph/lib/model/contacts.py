# -*- coding: utf-8 -*-
import sqlalchemy as sa
from sqlalchemy.dialects.mysql import BIGINT
from sqlalchemy.orm.exc import NoResultFound, MultipleResultsFound
from morph.lib.model.base import Base


class Contacts(Base):
    """
    联系人数据
    """
    __tablename__ = "contacts"

    id = sa.Column(BIGINT(unsigned=True), primary_key=True, autoincrement=True)
    user_id = sa.Column(BIGINT(unsigned=True), nullable=False)
    name = sa.Column(sa.String(45))
    origin_id = sa.Column(sa.String(45), nullable=False)
    group_id = sa.Column(BIGINT(unsigned=True))
    type = sa.Column(sa.String(24), nullable=False)
    platform = sa.Column(sa.String(24), nullable=False)

    @classmethod
    def create(cls, session, **kwargs):
        contacts = cls()
        for key, value in kwargs.items():
            setattr(contacts, key, value)
        session.add(contacts)
        session.commit()
        return contacts

    @classmethod
    def update(cls, session, contacts, upsert=True, **kwargs):
        if not contacts and not upsert:
            return False
        contacts = contacts or cls()
        for key, value in kwargs.items():
            setattr(contacts, key, value)
        session.add(contacts)
        session.commit()
        return contacts

    @classmethod
    def remove(cls, session, contacts_id=None, contacts=None):
        if not contacts and not contacts_id:
            return False
        if not contacts:
            contacts = cls.find_by_id(session, contacts_id)
        session.delete(contacts)
        session.commit()

    @classmethod
    def bulk_remove(cls, session, user_id):
        if not user_id:
            return False
        session.query(cls).filter(cls.user_id == user_id).delete()
    
    @classmethod
    def find_by_id(cls, session, contacts_id):
        try:
            return session.query(cls).filter(cls.id == contacts_id).one()
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

    @classmethod
    def find_by_group_id(cls, session, group_id, user_id):
        try:
            return session.query(cls).filter(sa.and_(cls.group_id == group_id, cls.user_id == user_id)).all()
        except NoResultFound:
            pass
        except MultipleResultsFound:
            pass
