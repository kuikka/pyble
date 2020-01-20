#! /usr/bin/env python3

"""
Copyright (c) 2020 Juha Kuikka
This file is part of pyble which is released under Modified BSD license
See LICENSE.txt for full license details
"""

import pyble
import struct
from gi.repository import GLib
from gi.repository import GObject

import logging
import binascii
import struct
import time
from influxdb import InfluxDBClient

INFLUX_SERVER = ('localhost', 8086)

TEMPERATURE_LABEL = 'temperature'
HUMIDITY_LABEL = 'humidity'

SENSOR_MAP = [ 
        {
            # Ruuvi #1
            'address': 'E6:99:94:26:C5:C3',
            'label': '{}',
            'tags': {
                'room': 'office',
                'location': 'window'
                }
        },
        {
            # Ruuvi #2
            'address': 'C1:2F:56:FB:6A:0A',
            'label': '{}',
            'tags': {
                'room': 'bedroom',
                'location': 'window'
                }
        },
        {
            # Ruuvi #3
            'address': 'F6:8C:F2:8D:6E:A3',
            'label': '{}',
            'tags': {
                'room': 'living',
                'location': 'tv'
                }
        },
        {
            # Mijia #1
            'address': '4C:65:A8:D4:03:E3',
            'label': '{}',
            'tags': {
                'room': 'hallway',
                'location': 'kitchen'
                }
        },
    ]

def send_sensor_data(points):
#    print(points)
    client = InfluxDBClient(host=INFLUX_SERVER[0], port=INFLUX_SERVER[1])
    client.switch_database('mydb')
    client.write_points(points)
    client.close()
    client = None

def update_sensor_data(dev, data):
    # Find device
    for sensor in SENSOR_MAP:
        if sensor['address'] == dev.Address:
            print("{}".format(sensor['tags']))
            json_body = []
            for datakey in data.keys():
                m = {
                        'measurement': datakey,
                        'tags': sensor['tags'],
                        'fields': {
                            'value': data[datakey]
                        }
                    }
                json_body.append(m)
            send_sensor_data(json_body)

#                label = sensor['label'].format(datakey)
#                tags = sensor['tags']
#                value = data[datakey]
#                timestamp = int(time.time())
#                s = "{};{} {} {}\n".format(label, tags, value, timestamp)
#                print(s)
#                send_sensor_data(bytes(s, 'ascii'))


def dbus_byte_array_to_bytes(array):
    ba = bytearray()
    for b in array:
        ba.append(b)
    return bytes(ba)



def parse_ruuvi_mfg_data(data):
    """
    Parse Ruuvi advertising formats
    see https://github.com/ruuvi/ruuvi-sensor-protocols/blob/master/broadcast_formats.md 
    and https://github.com/ruuvi/ruuvi-sensor-protocols/blob/master/dataformat_05.md
    for details

    >>> parse_ruuvi_mfg_data(b'\\x05\\x0f\\xfa6\\xc9\\xc6\\xda\\xff\\xe8\\x00\\x18\\x04\\x00\\xb5\\xf6-\\x0f-\\xe6\\x99\\x94&\\xc5\\xc3')
    {'Temperature': 20.45, 'Humidity': 35.0625, 'AtmoPressure': 1009.06, 'BatteryVoltage': 3.055, 'TxPower': 4}
    """

    if len(data) < 1:
        return

    fmt = data[0]
    if fmt == 5 and len(data) >= 15:
        temperature, humidity, atm_pressure = struct.unpack_from(">hHH", data, offset=1)
        power_info, = struct.unpack_from(">H", data, offset=13)

        battery_voltage_mv = power_info >> 5
        tx_power = power_info & 0x1F
        return {
                # degrees celsius
                TEMPERATURE_LABEL: temperature * 0.005,
                # Percent
                HUMIDITY_LABEL: humidity * 0.0025,
                # hPa
                'atmospheric_pressure': float(atm_pressure + 50000) / 100,
                # Volts
                'battery_voltage': float(battery_voltage_mv + 1600) / 1000,
                # dBm
                'tx_power': -40 + 2 * tx_power
                }

    return {}

def parse_mijia_sensor_data(data):
    """
    Parse Xiaomi Mijia Bluetooth temperature and humidity sensor data
    Based on info from https://github.com/mspider65/Xiaomi-Mijia-Bluetooth-Temperature-and-Humidity-Sensor

    >>> parse_mijia_sensor_data(b'P \\xaa\\x01\\x15\\xe3\\x03\\xd4\\xa8eL\\r\\x10\\x04\\xc9\\x00\\xc5\\x01')
    {'Temperature': 20.1, 'Humidity': 45.3}
    """

    if len(data) < 12:
        return

    ret = {}

    data_type, = struct.unpack_from("<B", data, offset=11)
    if data_type == 0x0D:
        temperature, humidity = struct.unpack_from("<HH", data, offset=14)
        ret[TEMPERATURE_LABEL] = temperature / 10
        ret[HUMIDITY_LABEL] = humidity /10
    elif data_type == 0x06:
        humidity, = struct.unpack_from("<H", data, offset=14)
        ret[HUMIDITY_LABEL] = humidity /10
    elif data_type == 0x04:
        temperature, = struct.unpack_from("<H", data, offset=14)
        ret[TEMPERATURE_LABEL] = temperature / 10
    elif data_type == 0x0A:
        battery, = struct.unpack_from("<B", data, offset=14)
        ret['battery_percent'] = battery

    return ret


def on_service_data_changed(dev, prop, val):
    #print('on_service_data_changed: {}: {}={}'.format(dev.Address , prop, val))
    if '0000fe95-0000-1000-8000-00805f9b34fb' in val:
        data = dbus_byte_array_to_bytes(val['0000fe95-0000-1000-8000-00805f9b34fb'])

        #print("SVC data fe95 found: {}".format(binascii.hexlify(data)))
        mijia_data = parse_mijia_sensor_data(data)
        #print(mijia_data)
        if len(mijia_data) > 0:
            update_sensor_data(dev, mijia_data)

def on_manufacturer_data_changed(dev, prop, val):
#    print('Device {}: {}={}'.format(dev.Address, prop, val))

    if 1177 in val:
        data = dbus_byte_array_to_bytes(val[1177])
        #print("MFG data 1177 found: {}".format(binascii.hexlify(data)))
        ruuvi_data = parse_ruuvi_mfg_data(data)
        #print(ruuvi_data)
        if len(ruuvi_data) > 0:
            update_sensor_data(dev, ruuvi_data)

def on_new_device(d):
    # print( 'on_new_device {}'.format(d))
    d.RegisterForPropertyChanged('ServiceData', on_service_data_changed)
    d.RegisterForPropertyChanged('ManufacturerData', on_manufacturer_data_changed)

    if d.Name == 'TI BLE Sensor Tag':
        print( 'found sensortag' )
        d.RegisterForPropertyChanged( 'Connected', sensortag_connected )
        d.RegisterForPropertyChanged( 'ServicesResolved', sensortag_connected )
        d.RegisterForPropertyChanged( 'GattServices', sensortag_connected )
        if d.Connected:
            print( 'already connected!' )
            sensortag_configure(d)
        else:
            d.Connect()

def on_device_added(d):
    #print( 'Device added: {}'.format(d))
    on_new_device(d)

def main():
    pyble.set_on_device_added_listener(on_device_added)

    for d in pyble.devices():
        on_new_device(d)

    print( 'Discovery starting' )
    for a in pyble.adapters():
        a.StartDiscovery(filter='le')

    print( 'Run mainloop!' )
    loop = GLib.MainLoop()
    loop.run()

if __name__ == "__main__":
    main()
