"""
Copyright (c) 2016 Juha Kuikka
This file is part of pyble which is released under Modified BSD license
See LICENSE.txt for full license details
"""

from pyble.DbusObject import DbusObject
from pyble.config import DEVICES

class Adapter(DbusObject):
    def __init__(self, path=None, device=None):
        if not device:
            device = 'hci0'

        if path:
            super().__init__(path, 'org.bluez.Adapter1')
        else:
            super().__init__('/org/bluez/' + device, 'org.bluez.Adapter1')

    def dump(self):
        props = self.properties.GetAll( 'org.bluez.Adapter1' )
        for p in props.keys():
            print( '  {}'.format(p) )

    def StartDiscovery(self, filter=None):
        if filter:
            self.proxy.SetDiscoveryFilter( { 'Transport': filter }, reply_handler=self.void_reply_handler, error_handler=self.error_handler )
        self.proxy.StartDiscovery(reply_handler=self.void_reply_handler, error_handler=self.error_handler)

    def devices(self):
        return [ DEVICES[path] for path in DEVICES.keys() if path.startswith(self.path) ]

