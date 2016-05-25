"""
Copyright (c) 2016 Juha Kuikka
This file is part of pyble which is released under Modified BSD license
See LICENSE.txt for full license details
"""

from pyble.DbusObject import DbusObject
from pyble.config import DESCRIPTORS

class GattCharacteristic(DbusObject):
    def __init__(self, path):
        super().__init__(path, 'org.bluez.GattCharacteristic1')

    def __repr__(self):
        return '{} ({}) UUID={}'.format(self._intf, self._path, self.UUID)

    def ReadValue(self):
        return self.proxy.ReadValue(reply_handler=self.void_reply_handler, error_handler=self.error_handler)

    def WriteValue(self, value):
        return self.proxy.WriteValue(value, reply_handler=self.void_reply_handler, error_handler=self.error_handler)

    def StartNotify(self):
        return self.proxy.StartNotify(reply_handler=self.void_reply_handler, error_handler=self.error_handler)

    def StopNotify(self):
        return self.proxy.StopNotify(reply_handler=self.void_reply_handler, error_handler=self.error_handler)

    # Return a list of the GattDescriptors this characteristic has
    def descriptors(self):
        return ( DESCRIPTORS[path] for path in DESCRIPTORS.keys() if path.startswith(self.path) )

    # Return a descriptor by UUID if it exists. In case of multiples first one found is returned.
    def descriptor(self, uuid):
        for d in self.descriptors():
            if d.UUID == uuid:
                return d

    def service(self):
        for path in SERVICES.keys():
            if self.path.startswith(path):
                return SERVICES[path]
