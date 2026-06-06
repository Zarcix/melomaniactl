#!/usr/bin/env python3
import dbus
import dbus.service
import dbus.mainloop.glib
import bluetooth
import socket

from gi.repository import GLib
from models import FeatureIds, Packet


BD_ADDR = "00:1F:F0:24:2D:AC"
UUID = "00001101-0000-1000-8000-00805f9b34fb"

# AABB CCDD EEEE FFFF G....G

# A = SOF always 0xFF
# B = GAIA protocol version
# C = Flags from Flag.java
# D = Packet Length
# E = Vendor ID found in VendorIDs.java IE 0b9e
# F = (Feature ID << 9) | (V3 Packet Type << 7) | (Actual ID)
# G = Payload

'''
ff04 0001 0b9e 02 00 00 - Gaming mode Off
ff04 0001 0b9e 00 0e 00 - Ambient Noise Off
ff04 0001 0b9e 00 0e 00

ff04 0000 0b9e 00 10 - Question, what is the current ANC mode
ff03 0001 0b9e 01 10 01 - Reply, ANC is set to 01 (ANC On)

ff04 0000 0b9e 02 01 - Question. what is the current gaming mode setting?
ff03 0001 0b9e 03 01 01 - Reply, Current Gaming mode setting is on

ff04 0001 0b9e 00 04 00 - Question, What is the Firmware Version?
ff03 0003 0b9e 01 04 01 03 00 ae - Reply, Firmware Version 1.3.0

ff04 0001 0b9e 00 03 00 - Question, what is the battery status
ff03 0009 0b9e 01 03 01 00 ff ff 37 ff ff 00 00 - Reply, Battery Status is 00 (not charging) and 37 (55% battery)

ff04 0000 0b9e 00 06 - Question, what is the current language?
ff03 0001 0b9e 01 06 00 - Reply, Language is currently Tones

ff04 0008 0b9e 00 06 00 00 00 00 00 00 00 00 - Question, what is the current language?
ff03 0001 0b9e 01 06 00 - Reply, Language is currently Tones

ff04 0000 0b9e 02 05
ff03 0002 0b9e 07 00 ff ff
'''

class BudsControlService(dbus.service.Object):
    def __init__(self, bus, object_path="/com/meloadapter/MeloControl"):
        super().__init__(bus, object_path)
        self.sock = None
        self.connect_device()

    def on_data_received(self, source, condition):
        buffer = bytearray()

        data = self.sock.recv(8 + 0xFF)
        if not data: return False
        buffer.extend(data)

        # Keep processing data in case multiple packets have been sent as 1
        while len(buffer) >= 8:
            if buffer[0] != 0xFF:
                buffer.pop(0)
                print("Invalid Packet. No SOF Value")

            payload_len = buffer[3]
            total_len = 8 + payload_len

            packet_hex = bytes(buffer[:total_len]).hex()
            del buffer[:total_len]

            packet = Packet.from_hex(packet_hex)
            print(packet)

        return True

    def connect_device(self):
        print(f"Discovering SPP service on {BD_ADDR}...")

        services = bluetooth.find_service(uuid=UUID, address=BD_ADDR)
        if not services:
            raise RuntimeError("No RFCOMM service found on this device")

        port = services[0]["port"]
        print(f"Connecting to {BD_ADDR} on RFCOMM port {port}...")

        self.sock = socket.socket(socket.AF_BLUETOOTH, socket.SOCK_STREAM, socket.BTPROTO_RFCOMM)
        self.sock.connect((BD_ADDR, port))

        self.sock.setblocking(False)
        GLib.io_add_watch(self.sock.fileno(), GLib.IO_IN, self.on_data_received)

        print("Connected successfully.")

    @dbus.service.method("com.meloadapter.MeloControl", in_signature="sss")
    # Payload Str: "int int int"
    def SendCommand(self, feature_str: str, subfeature_str: str, payload_str: str):
        feature = FeatureIds.from_name(feature_str)
        subfeature = feature.subfeature_cls.from_name(subfeature_str)
        payload = [int(val) for val in payload_str.split(" ")] if payload_str != "" else []

        packet = Packet.from_command(feature, subfeature, payload)
        payload = packet.to_hex()
        self.sock.send(payload)

    @dbus.service.method("com.meloadapter.MeloControl")
    def Disconnect(self):
        if self.sock:
            self.sock.close()
            self.sock = None
            print("Device disconnected.")

def main():
    dbus.mainloop.glib.DBusGMainLoop(set_as_default=True)
    bus = dbus.SessionBus()

    # <<< REQUEST A BUS NAME
    bus_name = dbus.service.BusName("com.meloadapter.MeloControl", bus=bus)
    service = BudsControlService(bus, object_path="/com/meloadapter/MeloControl")

    loop = GLib.MainLoop()
    print("MeloControl DBus service running...")
    loop.run()

if __name__ == "__main__":
    main()