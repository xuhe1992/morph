# -*- coding: utf-8 -*-

'''
© 2012-2013 eBay Software Foundation
Authored by: Tim Keefer
Licensed under CDDL 1.0
'''

import os
import yaml

from ebaysdk import log
from ebaysdk.exception import ConnectionConfigError

class Config(object):
    """Config Class for all APIs connections

    >>> c = Config(domain='api.ebay.com')
    >>> print(c.file())
    ebay.yaml
    >>> c.set('fname', 'tim')
    >>> c.get('fname')
    'tim'
    >>> c.get('missingkey', 'defaultvalue')
    'defaultvalue'
    >>> c.set('number', 22)
    >>> c.get('number')
    22
    """

    def __init__(self, domain, connection_kwargs=dict(), config_file='ebay.yaml'):
        self.config_file=config_file
        self.domain=domain
        self.values=dict()
        self.config_file_used=[]
        self.connection_kwargs=connection_kwargs

        # populate defaults        
        self._populate_yaml_defaults()

    def _populate_yaml_defaults(self):
        "Returns a dictionary of YAML defaults."

        # check for absolute path
        if self.config_file and os.path.exists(self.config_file):
            self.config_file_used=self.config_file
            fhandle = open(self.config_file, "r")
            dataobj = yaml.load(fhandle.read())

            for k, val in dataobj.get(self.domain, {}).items():
                self.set(k, val)

            return self

        # check other directories
        dirs = ['.', os.path.expanduser('~'), '/etc']
        for mydir in dirs:
            myfile = "%s/%s" % (mydir, self.config_file)

            if os.path.exists(myfile):
                self.config_file_used=myfile

                fhandle = open(myfile, "r")
                dataobj = yaml.load(fhandle.read())

                for k, val in dataobj.get(self.domain, {}).items():
                    self.set(k, val)

                return self

        if self.config_file:
            raise ConnectionConfigError('config file %s not found' % self.config_file)

    def file(self):
        return self.config_file_used

    def get(self, c_key, default_value=None):
        return self.values.get(c_key, default_value)

    def set(self, c_key, default_value, force=False):
        
        if force:
            self.values.update({c_key: default_value})
                    
        elif c_key in self.connection_kwargs and self.connection_kwargs[c_key] is not None:
            self.values.update({c_key: self.connection_kwargs[c_key]})

        else:
            if c_key not in self.values:
                self.values.update({c_key: default_value})
            else:
                pass
