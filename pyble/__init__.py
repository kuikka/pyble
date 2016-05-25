"""
Copyright (c) 2016 Juha Kuikka
This file is part of pyble which is released under Modified BSD license
See LICENSE.txt for full license details
"""

def adapters():
    from pyble.config import ADAPTERS
    return ( d for d in ADAPTERS.values() )

def devices():
    from pyble.config import DEVICES
    return ( d for d in DEVICES.values() )

def services():
    from pyble.config import SERVICES
    return ( s for s in SERVICES.values() )

def characteristics():
    from pyble.config import CHARACTERISTICS
    return ( c for c in CHARACTERISTICS.values() )

def descriptors():
    from pyble.config import DESCRIPTORS
    return ( d for d in DESCRIPTORS.values() )

def get_service( service_uuid ):
    for s in SERVICES.values():
        if s.UUID == service_uuid:
            return s

def get_characteristic( char_uuid, service_uuid=None ):
    from pyble.config import CHARACTERISTICS
    if service_uuid:
        s = get_service( service_uuid )
        if not s:
            return None
        return s.get_characteristic( char_uuid )
    else:
        for c in CHARACTERISTICS.values():
            if c.UUID == char_uuid:
                return c

initialized = False

if not initialized:
    initialized = True
    from pyble.objects import init
    init()

def set_on_device_added_listener(listener):
    from pyble.config import on_device_added
    on_device_added = listener

