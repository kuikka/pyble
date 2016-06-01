"""
Copyright (c) 2016 Juha Kuikka
This file is part of pyble which is released under Modified BSD license
See LICENSE.txt for full license details
"""

import sys
from pyble.Adapter import Adapter
from pyble.BleDevice import BleDevice
from pyble.GattDescriptor import GattDescriptor
from pyble.GattService import GattService
from pyble.GattCharacteristic import GattCharacteristic
from pyble.config import DEVICES, SERVICES, CHARACTERISTICS, DESCRIPTORS, ADAPTERS

this = sys.modules['pyble']

def create_existing_objects(manager):
    objects = manager.GetManagedObjects()
    for path in objects.keys():
#        dump_object( path, objects[path] )
        interfaces = objects[path]
        for interface in interfaces.keys():
            create_object(interface, path)

def create_object(interface, path):
    if interface == 'org.bluez.Device1':
        create_device( path )
    elif interface == 'org.bluez.GattService1':
        create_gatt_service( path )
    elif interface == 'org.bluez.GattCharacteristic1':
        create_gatt_characteristic( path )
    elif interface == 'org.bluez.GattDescriptor1':
        create_gatt_descriptor( path )
    elif interface == 'org.bluez.Adapter1':
        create_adapter( path )

def create_adapter(path):
    adapter = Adapter( path=path )
    ADAPTERS[ path ] = adapter

def create_device(path):
    dev = BleDevice( path )
    DEVICES[ path ] = dev
    if this.on_device_added:
        this.on_device_added(dev)

def create_gatt_service(path):
    service = GattService(path)
    SERVICES[ path ] = service

def create_gatt_characteristic(path):
    char = GattCharacteristic(path)
    CHARACTERISTICS[ path ] = char

def create_gatt_descriptor(path):
    desc = GattDescriptor(path)
    DESCRIPTORS[ path ] = desc

def dump_object(path, interfaces_and_properties):
    print( 'Object: {}:'.format( path ) )
    for interface in interfaces_and_properties.keys():
        print( '  Interface: {}'.format( interface) )
        for property in interfaces_and_properties[ interface ]:
            print( '    {}: {}'.format( property, interfaces_and_properties[ interface ][ property ] ) )

# OBJPATH object_path, DICT<STRING,DICT<STRING,VARIANT>> interfaces_and_properties);
def new_object(path, interfaces_and_properties):
    print( 'new_object: {}, interfaces: {}'.format(path, ', '.join(interfaces_and_properties.keys())))
    for interface in interfaces_and_properties.keys():
        create_object(interface,path)

def init():
    import dbus
    from dbus.mainloop.glib import DBusGMainLoop
    DBusGMainLoop(set_as_default=True)
    bus = dbus.SystemBus()
    manager = dbus.Interface(bus.get_object("org.bluez", "/"),
                     "org.freedesktop.DBus.ObjectManager")

    manager.connect_to_signal( 'InterfacesAdded', new_object )
    create_existing_objects(manager)
