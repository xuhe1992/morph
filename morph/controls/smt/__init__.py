# -*- coding: utf-8 -*-

"""
@author: xuhe
@date: 17/3/31
@description: 
"""

from morph.lib.model.user import User
from morph.controls import CustomerControls


class SmtCustomer(CustomerControls):

    def __init__(self, **kwargs):
        user = User()
        CustomerControls.__init__(self, user, kwargs)

