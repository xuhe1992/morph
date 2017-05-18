# -*- coding: utf-8 -*-

"""
@author: xuhe
@date: 17/5/17
@description: 
"""

from morph.lib.model.base import db, metadata
from morph.lib.model.attachment import Attachment
from morph.lib.model.channel import Channel
from morph.lib.model.message import Message


class InitMysql(object):

    def __init__(self):
        pass

    @classmethod
    def create_tables(cls):
        metadata.create_all(db)