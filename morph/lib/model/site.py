# -*- coding=utf-8 -*-

"""
@author:lance
@date:
@version:
@description:
"""

import sqlalchemy as SA
from furion.lib.model.base import Base


class Site(Base):

    __tablename__ = "site"

    id = SA.Column(SA.INTEGER, primary_key=True, autoincrement=True)
    lang = SA.Column(SA.String(8), nullable=False)
    currency = SA.Column(SA.String(8), nullable=False)
    url = SA.Column(SA.String(64), nullable=False)
    tag = SA.Column(SA.String(32), nullable=False)
    name = SA.Column(SA.String(32), nullable=False)
    country = SA.Column(SA.String(32), nullable=False)
    netloc = SA.Column(SA.String(64), nullable=False)
    platform_id = SA.Column(SA.INTEGER, SA.ForeignKey("platform.id"), nullable=False)

    @classmethod
    def find_by_id(cls, session, site_id):
        site = session.query(cls).filter(cls.id == site_id).first()
        return site

    @classmethod
    def find_by_netloc(cls, session, netloc):
        site = session.query(cls).filter(cls.netloc == netloc).first()
        return site
    
    @classmethod
    def find_by_platform_id(cls, session, platform_id):
        return session.query(cls).filter(cls.platform_id == platform_id).all()

    @classmethod
    def find_by_platform_country(cls, session, country, platform_id):
        site = session.query(cls).filter(
            SA.and_(
                cls.country == country,
                cls.platform_id == platform_id
            )).first()
        return site

    @classmethod
    def find_by_country_lang(cls, session, country, lang):
        site = session.query(cls).filter(
            SA.and_(
                cls.country == country,
                cls.lang == lang
            )).first()
        return site

    @classmethod
    def find_by_platform_name(cls, session, name, platform_id):
        site = session.query(cls).filter(
            SA.and_(
                cls.name == name,
                cls.platform_id == platform_id
            )).first()
        return site

    def to_json(self):
        return {
            "id": self.id,
            "lang": self.lang,
            "currency": self.currency,
            "name": self.name,
            "platform_id": self.platform_id,
            "url": self.url,
            "country": self.country,
            "tag": self.tag,
            "netloc": self.netloc
        }
    
    @classmethod
    def to_object(cls, site):
        return cls(
            id=site["id"],
            lang=site["lang"],
            currency=site["currency"],
            url=site["url"],
            tag=site["tag"],
            name=site["name"],
            country=site["country"],
            netloc=site["netloc"],
            platform_id=site["platform_id"]
        )


