# -*- coding: utf-8 -*-

"""
@author: xuhe
@date: 17/1/16
@description: 
"""

import contextlib
from sqlalchemy.orm import sessionmaker
from morph.lib.model.base import db


session_maker = sessionmaker(bind=db)


def get_session():
    """
    链接到数据库的SESSION
    """
    return session_maker()


@contextlib.contextmanager
def sessionCM():
    session = get_session()
    try:
        yield session
    except Exception, e:
        raise e
    finally:
        session.close()