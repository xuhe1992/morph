# -*- coding=utf-8 -*-

"""
@author:lance
@date:
@version:
@description:
"""

import sqlalchemy as SA
from sqlalchemy.dialects.mysql import BIGINT
from sqlalchemy.orm import relationship
from morph.lib.model.base import Base
from morph.lib.model.session import sessionCM
from sqlalchemy.orm.exc import MultipleResultsFound, NoResultFound
import hashlib
from morph.lib.utils.logger_util import logger
from morph.lib.model.manage import Management


class Shop(Base):

    __tablename__ = "shop"

    id = SA.Column(BIGINT(unsigned=True), primary_key=True, autoincrement=True)
    name = SA.Column(SA.String(64), nullable=False, default="ActNeed")
    platform = SA.Column(SA.String(30), nullable=False)
    owner = SA.Column(SA.String(64), nullable=False)
    account = SA.Column(SA.String(1024), nullable=True)
    session = SA.Column(SA.String(1024), nullable=True)
    site_id = SA.Column(SA.INTEGER, nullable=False)

    managements = relationship("Management", backref="shop", cascade="delete")

    @classmethod
    def create(cls, platform, site, step, name=None):
        with sessionCM() as session:
            try:
                shop = session.query(cls).filter(SA.and_(cls.platform == platform, cls.site == site)).one()
                return shop
            except NoResultFound:
                shop = cls()
                shop.name = name if name else cls.generate_shop_name(platform, site)
                shop.platform = platform
                shop.site = site
                shop.step = step
                session.add(shop)
                session.commit()
                return shop
            except Exception, e:
                logger.error(e)
                return None

    @classmethod
    def find_all(cls, session):
        return session.query(cls).filter().all()

    @classmethod
    def update(cls, session, shop):
        session.add(shop)
        session.commit()

    @classmethod
    def find_by_id(cls, session, shop_id):
        try:
            return session.query(cls).filter(cls.id == shop_id).one()
        except MultipleResultsFound:
            return None
        except NoResultFound:
            return None

    @classmethod
    def find_by_name(cls, session, shop_name):
        try:
            return session.query(cls).filter(cls.name == shop_name).all()
        except MultipleResultsFound:
            # return None
            return "Multiple"
        except NoResultFound:
            return None

    @classmethod
    def generate_shop_name(cls, platform, site):
        raw_str = platform + site
        md5 = hashlib.md5()
        md5.update(raw_str)
        return md5.hexdigest()

    @classmethod
    def get_session_token(cls, session, shop_id):
        shop = session.query(cls).filter(cls.id == shop_id).one()
        shop_session = shop.session
        shop_account = shop.account
        return shop_session, shop_account

    @classmethod
    def get_count(cls, session):
        return session.query(cls).count()

    @classmethod
    def get_count_filter(cls, session, filters):
        if len(str(filters)):
            count = session.query(cls).filter(filters).count()
        else:
            count = session.query(cls).count()
        return count

    @classmethod
    def find_with_skip_limit(cls, session, filters, start, stop):
        if len(str(filters)):
            return session.query(cls).filter(filters).slice(start, stop).all()
        else:
            return session.query(cls).slice(start, stop).all()

    @classmethod
    def delete_shop(cls, session, shop_id):
        shop = session.query(cls).filter(cls.id == shop_id).first()
        session.delete(shop)
        session.commit()

    @classmethod
    def find_by_owner(cls, session, owner):
        shop = session.query(cls).filter(cls.owner == owner).first()
        if shop:
            return shop, [m.user_id for m in shop.managements]
        else:
            return False

    @classmethod
    def find_like_by_owner(cls, session, owner):
        shop = session.query(cls).filter(cls.owner.like(owner+"%")).first()
        if shop:
            return shop, [m.user_id for m in shop.managements]
        else:
            return False

    @classmethod
    def find_by_site_owner(cls, session, owner, site_id):
        shop = session.query(cls).filter(
            SA.and_(
                cls.owner == owner,
                cls.site_id == site_id
            )
        ).first()
        if shop:
            return shop, [m.user_id for m in shop.managements]
        else:
            return False

    @classmethod
    def find_all_by_owner(cls, session, owner):
        return session.query(cls).filter(cls.owner == owner).all()

    def to_json(self):
        return {
            "id": self.id,
            "name": self.name,
            "platform": self.platform,
            "owner": self.owner,
            "session": self.session,
            "account": self.account,
            "site_id": self.site_id
        }

    @classmethod
    def to_object(cls, shop):
        return cls(
            id=shop["id"],
            name=shop["name"],
            platform=shop["platform"],
            owner=shop["owner"],
            session=shop["session"],
            account=shop["account"],
            site_id=shop["site_id"]
        )

    @classmethod
    def get_every_day_count(cls, session, start, end):
        between = Shop.create_date.between(start, end)
        cursor = session.query(cls.create_date).filter(between).group_by(cls.create_date)
        count_dict = dict()
        for record in cursor:
            date_key = record[0].strftime("%Y-%m-%d")
            if date_key in count_dict:
                count_dict[date_key] += 1
            else:
                count_dict[date_key] = 1
        return count_dict

