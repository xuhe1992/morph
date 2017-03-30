# -*- coding:utf-8 -*-

__author__ = 'Administrator'


import os
import yaml


class Config(object):
    def __init__(self, domain, config_file='wish.yaml'):
        self.config_file = config_file
        self.domain = domain
        self.values = dict()

        self._populate_yaml_defaults()

    def _populate_yaml_defaults(self):
        """
        Returns a dictionary of YAML defaults.
        """
        if self.config_file and os.path.exists(self.config_file):
            self.config_file_used = self.config_file
            file_handle = open(self.config_file, "r")
            data_obj = yaml.load(file_handle.read())

            for k, val in data_obj.get(self.domain, {}).items():
                self.set(k, val)

    def set(self, key, value):
        """
        Set a key-value into Config.values
        """
        self.values.update({key: value})

    def get(self, key):
        """
        :return: a value when key in Config.values
        """
        return self.values[key]