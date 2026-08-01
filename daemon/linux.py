#!/usr/bin/env python3
import dbus
import dbus.service
import dbus.mainloop.glib
import bluetooth
import socket

from gi.repository import GLib
from api import FeatureIds, Packet

BD_ADDR = "00:1F:F0:24:2D:AC"
DEVICE_PATH = f"/org/bluez/hci0/dev_{BD_ADDR.replace(':', '_')}"
UUID = "00001101-0000-1000-8000-00805f9b34fb"

MAX_BACKOFF = 32

class MeloControlService(dbus.service.Object):
    def __init__(self, bus, object_path="/com/meloadapter/MeloControl"):
        super().__init__(bus, object_path)
        self.sock = None
        self.bus = bus

        self.system_bus = dbus.SystemBus()
        self.system_bus.add_signal_receiver(
            self.on_properties_changed,
            bus_name="org.bluez",
            signal_name="PropertiesChanged",
            path=DEVICE_PATH,
            dbus_interface="org.freedesktop.DBus.Properties"
        )

        self.Connect()

    def on_properties_changed(self, interface, changed, invalidated):
        if "Connected" in changed:
            is_connected = changed["Connected"]
            if not is_connected and self.sock:
                print("BlueZ signaled disconnection.")
                self.Disconnect()
            elif is_connected and not self.sock:
                print("BlueZ signaled connection. Re-initializing socket...")
                self.Connect()

    def on_data_received(self, source, condition):
        buffer = bytearray()

        try:
            data = self.sock.recv(8 + 0xFF)
            if not data:
                self.Disconnect()
                return False
        except BlockingIOError:
            return True
        except Exception as e:
            print(f"Unexpected error: {e}")
            self.Disconnect()
            return False

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
            self.CommandReceived(
                packet.packet_dir.name,
                packet.flags.name,
                packet.packet_type.name,
                packet.feature_id.name,
                packet.subfeature_id.name,
                ",".join(str(pl) for pl in packet.payload),
            )

        return True

    @dbus.service.signal("com.meloadapter.MeloControl", signature="ssssss")
    def CommandReceived(self, direction: str, flags: str, type: str, feature: str, subfeature: str, payload: str):
        pass

    @dbus.service.method("com.meloadapter.MeloControl", in_signature="sss")
    # Payload Str: "int int int"
    def SendCommand(self, feature_str: str, subfeature_str: str, payload_str: str):
        feature = FeatureIds.from_name(feature_str)
        subfeature = feature.subfeature_cls.from_name(subfeature_str)
        payload = [int(val) for val in payload_str.split(" ")] if payload_str != "" else []

        packet = Packet.from_command(feature, subfeature, payload)
        print(packet)
        payload = packet.to_hex()
        self.sock.send(payload)

    @dbus.service.method("com.meloadapter.MeloControl", out_signature="a{sas}")
    def GetFeatures(self, query: str = ""):
        result = {}

        query = query.strip().lower()

        for feature in FeatureIds:
            feature_name = feature.name

            # optional filter
            if query and query not in feature_name.lower():
                continue

            result[feature_name] = [
                s.name for s in feature.subfeature_cls
            ]

        return result
    
    def Connect(self):
        """Entry point for connection, initiates the non-blocking retry loop."""
        self.retry_attempt = 0
        self._attempt_connection()
        self.ConnectionChanged()

    def _attempt_connection(self):
        try:
            print(f"Discovering SPP service on {BD_ADDR}...")
            services = bluetooth.find_service(uuid=UUID, address=BD_ADDR)
            
            if not services:
                raise RuntimeError("Service not found")

            port = services[0]["port"]
            self.sock = socket.socket(socket.AF_BLUETOOTH, socket.SOCK_STREAM, socket.BTPROTO_RFCOMM)
            self.sock.connect((BD_ADDR, port))
            self.sock.setblocking(False)
            
            GLib.io_add_watch(self.sock.fileno(), GLib.IO_IN, self.on_data_received)
            print("Connected successfully.")
            self.retry_attempt = 0
            
        except Exception as e:
            self.retry_attempt += 1
            delay = min(2 ** self.retry_attempt, MAX_BACKOFF)
            
            print(f"Connection failed: {e}. Retrying in {delay}s...")
            GLib.timeout_add_seconds(delay, self._attempt_connection)
            return False

    @dbus.service.method("com.meloadapter.MeloControl")
    def Disconnect(self):
        if self.sock:
            self.sock.close()
            self.sock = None
            print("Device disconnected.")

        self.ConnectionChanged()

    @dbus.service.method("com.meloadapter.MeloControl", out_signature="b")
    def ConnectionStatus(self):
        return self.sock != None

    @dbus.service.signal("com.meloadapter.MeloControl")
    def ConnectionChanged(self):
        pass

def main():
    dbus.mainloop.glib.DBusGMainLoop(set_as_default=True)
    bus = dbus.SessionBus()

    # <<< REQUEST A BUS NAME
    bus_name = dbus.service.BusName("com.meloadapter.MeloControl", bus=bus)
    service = MeloControlService(bus, object_path="/com/meloadapter/MeloControl")

    loop = GLib.MainLoop()
    print("MeloControl DBus service running...")
    loop.run()

if __name__ == "__main__":
    main()