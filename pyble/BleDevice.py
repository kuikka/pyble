"""
Copyright (c) 2016 Juha Kuikka
This file is part of pyble which is released under Modified BSD license
See LICENSE.txt for full license details
"""

from pyble.DbusObject import DbusObject
from pyble.config import SERVICES

class BleDevice(DbusObject):
    def __init__(self, path):
        super().__init__(path, 'org.bluez.Device1')

    # Connect to this device
    def Connect(self):
        self.proxy.Connect(reply_handler=self.void_reply_handler, error_handler=self.error_handler)

    # Disconnect to this device
    def Disconnect(self):
        self.proxy.Disconnect(reply_handler=self.void_reply_handler, error_handler=self.error_handler)

    # Return a list of the GattServices this device has
    def services(self):
        return [ SERVICES[path] for path in SERVICES.keys() if path.startswith(self.path) ]

    @property
    def ServicesResolved(self):
        # Work around the experimental BLE interface
        properties = self.properties.GetAll( self._intf )
        if 'ServicesResolved' in properties.keys():
            return properties[ 'ServicesResolved' ]
        elif 'GattServices' in properties:
            return len( properties[ 'GattServices' ] ) > 0
