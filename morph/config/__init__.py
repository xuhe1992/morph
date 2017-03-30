# -*- coding: utf-8 -*-

"""
@author: xuhe
@date: 17/3/30
@description: 
"""

import os
from morph.config import development
from morph.config import production
from morph.lib.utils.configure_object import dict_from_model
from morph.lib.utils.dict2object import Dict2Obj


default_env = "development"

execute_env = os.environ.get("MORPH_ENV", default_env)

if execute_env.lower() in ["production"]:
    config = production
else:
    config = development

settings = Dict2Obj(dict_from_model(config))
settings.configure("EXECUTE_ENV", execute_env)

del execute_env
