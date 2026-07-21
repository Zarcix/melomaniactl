from gi.repository import Gtk, Adw, GLib
import sys
import time

from parsers.misc.device import ConnectedDevice

from util import convert_list_payload
from .base import BaseModule

class ConnectionsModule(BaseModule):
    def __init__(self, window):
        self.connected_devices: set[ConnectedDevice] = set()
        self.device_rows = []
        super().__init__(window)

    def setup_callbacks(self):
        self.dbus.on_event("MISC", "GET_DEVICES", self.connections_update)
        self.dbus.on_event("MISC", "CONNECT_DEVICE", self.connections_changed)
        self.dbus.on_event("MISC", "DISCONNECT_DEVICE", self.connections_changed)
        self.refresh_data()

    def setup_ui(self) -> Adw.Clamp:
        # Create the group to hold the info in a framed/boxed style
        self.group = Adw.PreferencesGroup(title="Connected Devices")

        # Create the refresh button
        refresh_btn = Gtk.Button(icon_name="view-refresh-symbolic")
        refresh_btn.set_tooltip_text("Refresh Device Information Module")
        refresh_btn.connect("clicked", self.refresh_data)
        refresh_btn.set_valign(Gtk.Align.CENTER)

        # Add the button to the group header
        self.group.set_header_suffix(refresh_btn)

        clamp = Adw.Clamp(maximum_size=400)
        clamp.set_child(self.group)

        self.setup_callbacks()

        return clamp
    
    def refresh_data(self, sender=None):
        # Clear devices since we performed a hard reset
        self.connected_devices.clear()
        self.dbus.send("misc", "GET_DEVICES")

        if sender is not None:
            toast = Adw.Toast.new("Refreshing Device Status...")
            self.window.toast.add_toast(toast)

    def connections_update(self, dir, flags, ptype, subf, pay):
        payload_list = convert_list_payload(pay)
        device = ConnectedDevice.parse(payload_list)
        if type(device) != ConnectedDevice:
            print(f"ConnectionsModule: Could not parse data: {pay}", file=sys.stderr)

        self.connected_devices.add(device)

        GLib.idle_add(self._rebuild_connection_list)

    def connections_changed(self, dir, flags, ptype, subf, pay):
        time.sleep(5)
        self.refresh_data()

    def _rebuild_connection_list(self):
        for row in self.device_rows:
            self.group.remove(row)
        self.device_rows.clear()

        if not self.connected_devices:
            empty_row = Adw.ActionRow(title="No devices found")
            self.group.add(empty_row)
            self.device_rows.append(empty_row)
            return
        
        for dev in sorted(list(self.connected_devices), key=lambda x: x.conn_id):
            clean_name = dev.dev_name.replace('\x00', '').strip()
            row = Adw.ActionRow(
                title=clean_name or f"Device ID: {dev.conn_id}",
                subtitle=f"ID: {dev.conn_id} - {':'.join(dev.mac_address).upper()}"
            )
            
            # Add status text indicator (e.g., Paired, Connected)
            status_text = dev.conn_status.name.title()
            status_label = Gtk.Label(label=status_text)
            status_label.set_valign(Gtk.Align.CENTER)
            status_label.add_css_class("dim-label")  # Optional: subtle styling
            row.add_suffix(status_label)

            action_btn = Gtk.Button()
            action_btn.set_valign(Gtk.Align.CENTER)

            if dev.is_connected():
                action_btn.set_label("Disconnect")
                action_btn.add_css_class("destructive-action")
                action_btn.connect("clicked", lambda btn, d=dev: self._disconnect_device(btn, d))
            else:
                action_btn.set_label("Connect")
                action_btn.add_css_class("suggested-action")
                action_btn.connect("clicked", lambda btn, d=dev: self._connect_device(btn, d))

            row.add_suffix(action_btn)
            
            # Add to group and track it
            self.group.add(row)
            self.device_rows.append(row)

    def _disconnect_device(self, button: Gtk.Button, device: ConnectedDevice):
        button.set_label("Disconnecting ...")
        button.set_sensitive(False)
        self.dbus.send("misc", "DISCONNECT_DEVICE", str(device.conn_id))

    def _connect_device(self, button: Gtk.Button, device: ConnectedDevice):
        button.set_label("Connecting ...")
        button.set_sensitive(False)
        self.dbus.send("misc", "CONNECT_DEVICE", str(device.conn_id))