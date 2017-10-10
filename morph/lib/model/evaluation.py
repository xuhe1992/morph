# -*- coding: utf-8 -*-
import sqlalchemy as sa
from sqlalchemy import and_
from sqlalchemy.dialects.mysql import BIGINT
from sqlalchemy.orm.exc import NoResultFound, MultipleResultsFound
from morph.lib.model.base import Base


class Evaluation(Base):
    """
    模板数据
    """
    __tablename__ = "evaluation"

    id = sa.Column(BIGINT(unsigned=True), primary_key=True, autoincrement=True)
    # title = sa.Column(sa.String(128), nullable=False)
    # content = sa.Column(sa.String(2048), nullable=False)
    # user_id = sa.Column(BIGINT(unsigned=True), sa.ForeignKey("user.id"), nullable=False)

    shop_id = sa.Column(BIGINT(unsigned=True))
    order_line_item_id = sa.Column(sa.String(64), nullable=False)
    status = sa.Column(sa.String(12), nullable=True)
    # feed_back_id = sa.Column(sa.String(64), nullable=True)
    # buyer_content = sa.Column(sa.String(1024), nullable=True)
    buyer_id = sa.Column(sa.String(64), nullable=True)
    # buyer_score = sa.Column(sa.String(12), nullable=True)
    item_id = sa.Column(sa.String(64), nullable=True)
    item_title = sa.Column(sa.String(128), nullable=True)
    seller_content = sa.Column(sa.String(1024), nullable=True)

    @classmethod
    def create(cls, session, **kwargs):
        evaluation = cls()
        for key, value in kwargs.items():
            setattr(evaluation, key, value)
        session.add(evaluation)
        session.commit()
        return evaluation

    @classmethod
    def update(cls, session, evaluation, upsert=True, **kwargs):
        if not evaluation and not upsert:
            return False
        evaluation = evaluation or cls()
        for key, value in kwargs.items():
            setattr(evaluation, key, value)
        session.add(evaluation)
        session.commit()
        return evaluation

    @classmethod
    def remove(cls, session, evaluation_id=None, evaluation=None):
        if not evaluation and not evaluation_id:
            return False
        if not evaluation:
            evaluation = cls.find_by_id(session, evaluation_id)
        session.delete(evaluation)
        session.commit()

    @classmethod
    def bulk_remove(cls, session, user_id):
        if not user_id:
            return False
        session.query(cls).filter(cls.user_id == user_id).delete()
    
    @classmethod
    def find_by_id(cls, session, evaluation_id):
        try:
            return session.query(cls).filter(and_(cls.id == evaluation_id, cls.status == "seller")).one()
        except NoResultFound:
            pass
        except MultipleResultsFound:
            pass

    @classmethod
    def find_by_order_line_id(cls, session, order_line_id):
        try:
            return session.query(cls).filter(cls.order_line_item_id == order_line_id).one()
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
