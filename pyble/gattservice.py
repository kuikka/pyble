"""
Copyright (c) 2016 Juha Kuikka
This file is part of pyble which is released under Modified BSD license
See LICENSE.txt for full license details
"""

from pyble import DbusObject
from __init__ import characteristics

class GattService(DbusObject):
    def __init__(self, path):
        super().__init__(path, 'org.bluez.GattService1')

    def __repr__(self):
        return '{} ({}) UUID={}'.format(self._intf, self._path, self.UUID)

    def characteristics(self):
        return [ characteristics[path] for path in characteristics.keys() if path.startswith(self.path) ]
