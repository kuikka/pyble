"""
Copyright (c) 2016 Juha Kuikka
This file is part of pyble which is released under Modified BSD license
See LICENSE.txt for full license details
"""

from pyble.DbusObject import DbusObject

class GattDescriptor(DbusObject):
    def __init__(self, path):
        super().__init__(path, 'org.bluez.GattDescriptor1')

    def __repr__(self):
        return '{} ({}) UUID={}'.format(self._intf, self._path, self.UUID)

