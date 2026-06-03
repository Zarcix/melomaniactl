#!/usr/bin/env python3
import dbus
import dbus.service
import dbus.mainloop.glib
from gi.repository import GLib
import bluetooth
import socket

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

'''


CONTROL_MAP = {
    "GAMING_MODE__N": "ff0400010b9e020000",
    "GAMING_MODE__Y": "ff04 0001 0b9e 02 00 01",

    "AMBIENT_NOISE_CONTROL__NORMAL": "ff0400010b9e000e00",
    "AMBIENT_NOISE_CONTROL__NOISE_CANCELLING": "ff0400010b9e000e01",
    "AMBIENT_NOISE_CONTROL__TRANSPARENCY": "ff0400010b9e000e02",

    "DYNA_EQ__N": "ff0400010b9e001400",
    "DYNA_EQ__Y": "ff0400010b9e001401",

    "WEAR_DETECTION__N": "ff0400010b9e020600",
    "WEAR_DETECTION__Y": "ff0400010b9e020601",
}

class BudsControlService(dbus.service.Object):
    def __init__(self, bus, object_path="/com/example/BudsControl"):
        super().__init__(bus, object_path)
        self.sock = None
        self.connect_device()

    def connect_device(self):
        print(f"Discovering SPP service on {BD_ADDR}...")
        services = bluetooth.find_service(uuid=UUID, address=BD_ADDR)
        if not services:
            raise RuntimeError("No RFCOMM service found on this device")
        port = services[0]["port"]
        print(f"Connecting to {BD_ADDR} on RFCOMM port {port}...")
        self.sock = socket.socket(socket.AF_BLUETOOTH, socket.SOCK_STREAM, socket.BTPROTO_RFCOMM)
        self.sock.connect((BD_ADDR, port))
        print("Connected successfully.")

    @dbus.service.method("com.example.BudsControl", in_signature="s")
    def SendCommand(self, cmd_name):
        if cmd_name not in CONTROL_MAP:
            raise ValueError(f"Unknown command: {cmd_name}")
        if not self.sock:
            raise RuntimeError("Device not connected")
        packet = bytes.fromhex(CONTROL_MAP[cmd_name])
        breakpoint()
        self.sock.send(packet)
        print(f"Sent {cmd_name}: {CONTROL_MAP[cmd_name]}")

    @dbus.service.method("com.example.BudsControl")
    def Disconnect(self):
        if self.sock:
            self.sock.close()
            self.sock = None
            print("Device disconnected.")

def main():
    dbus.mainloop.glib.DBusGMainLoop(set_as_default=True)
    bus = dbus.SessionBus()

    # <<< REQUEST A BUS NAME
    bus_name = dbus.service.BusName("com.example.BudsControl", bus=bus)
    service = BudsControlService(bus, object_path="/com/example/BudsControl")

    loop = GLib.MainLoop()
    print("BudsControl DBus service running...")
    loop.run()

if __name__ == "__main__":
    main()