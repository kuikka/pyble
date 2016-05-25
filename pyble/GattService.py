"""
Copyright (c) 2016 Juha Kuikka
This file is part of pyble which is released under Modified BSD license
See LICENSE.txt for full license details
"""

from pyble.DbusObject import DbusObject
from pyble.config import CHARACTERISTICS

class GattService(DbusObject):
    def __init__(self, path):
        super().__init__(path, 'org.bluez.GattService1')

    def __repr__(self):
        return '{} ({}) UUID={}'.format(self._intf, self._path, self.UUID)

    # Return a list of the GattCharacteristics this service has
    def characteristics(self):
        return ( CHARACTERISTICS[path] for path in CHARACTERISTICS.keys() if path.startswith(self.path) )

    # Return a characteristic by UUID if it exists. In case of multiples first one found is returned
    def characteristic(self, uuid):
        for c in self.characteristics():
            if c.UUID == uuid:
                return c

    # Returns the BleDevice this service is on
    def device(self):
        for path in DEVICES.keys():
            if self.path.startswith(path):
                return DEVICES[path]
        

