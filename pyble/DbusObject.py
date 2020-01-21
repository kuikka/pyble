"""
Copyright (c) 2016 Juha Kuikka
This file is part of pyble which is released under Modified BSD license
See LICENSE.txt for full license details
"""

import dbus

class DbusObject(object):
    def __init__(self, path, intf):
        self.bus = dbus.SystemBus()

        self._path = str(path)
        self._intf = intf
        self.property_cb = {}
        self.proxy = dbus.Interface(
                self.bus.get_object('org.bluez', self.path),
                intf)
        self.properties = dbus.Interface(
                self.bus.get_object('org.bluez', self.path),
                'org.freedesktop.DBus.Properties')

        self.signal = None

    def __repr__(self):
        return '{}({})'.format(self._intf, self._path)

    def __getattr__(self, name):
        if 'properties' in self.__dict__.keys() and name in self.properties.GetAll( self._intf ).keys():
            return self.properties.Get( self._intf, name )

    def __setattr__(self, name, value):
        if self.properties and name in self.properties.GetAll( self._intf ).keys():
            return self.properties.Set( self._intf, name, value )
        else:
            super().__setattr__( name, value )

    @property
    def path(self):
        return str(self._path)

    def OnPropertiesChanged(self, interface, changed_properties, invalidated_properties):
#        print( 'OnPropertiesChanged {} {} {} {}'.format(
#            self, interface, changed_properties, invalidated_properties ))
        for prop in changed_properties.keys():
            l = self.property_cb.get(prop, list())
            for cb in l:
                cb(self, prop, changed_properties[prop])

    def RegisterForPropertyChanged(self, property_value, cb):
        # Register for PropertiseChanged
        if self.signal is None:
            self.signal = self.properties.connect_to_signal( 'PropertiesChanged', self.OnPropertiesChanged)

        l = self.property_cb.get(property_value, list())
        l.append(cb)
        self.property_cb[property_value] = l

    def error_handler(self, err):
        print( 'Dbusobject({}) error: {}'.format(self.path, err))

    def void_reply_handler(self):
        pass
        #print( 'Dbusobject){}) reply'.format(self.path))

    def close(self):
        if self.signal is not None:
            self.signal.remove()
        self.property_cb.clear()
