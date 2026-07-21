from .base import BaseModule
from gi.repository import Gtk, Adw, GLib
from parsers.misc.battery_state import BatteryState
from parsers.misc.manufacturer import Manufacturer
from parsers.misc.model import Model
from parsers.misc.firmware_version import FirmwareVersion

from util import convert_list_payload

BATTERY_DISPLAY_CONFIG = {
    "Melomania P100 SE": {
        "display_fields": ["left_percent"],
        "labels": {"left_percent": "Battery"}
    },
    "Default": {
        "display_fields": ["left_percent", "right_percent", "case_percent"],
        "labels": {"left_percent": "L", "right_percent": "R", "case_percent": "Case"}
    }
}

class DeviceInfoModule(BaseModule):
    def _setup_manufacturer_row(self):
        self.mfg_row = Adw.ActionRow(title="Manufacturer")
        self.mfg_label = Gtk.Label(label="Loading...")
        self.mfg_row.add_suffix(self.mfg_label)
        self.group.add(self.mfg_row)

    def _setup_model_row(self):
        self.model_row = Adw.ActionRow(title="Device Model")
        self.model_label = Gtk.Label(label="Loading...")
        self.model_row.add_suffix(self.model_label)
        self.group.add(self.model_row)

    def _setup_battery_row(self):
        self.battery_row = Adw.ActionRow(title="Battery")
        self.battery_label = Gtk.Label(label="Loading...")
        self.battery_row.add_suffix(self.battery_label)
        self.group.add(self.battery_row)

    def _setup_firmware_row(self):
        self.firmware_row = Adw.ActionRow(title="Firmware Version")
        self.firmware_label = Gtk.Label(label="Loading...")
        self.firmware_row.add_suffix(self.firmware_label)
        self.group.add(self.firmware_row)

    def _setup_callbacks(self):
        self.dbus.on_event("MISC", "GET_BATTERY_STATE", self.battery_update)
        self.dbus.on_event("MISC", "GET_MANUFACTURER", self.manufacturer_update)
        self.dbus.on_event("MISC", "GET_MODEL", self.model_update)
        self.dbus.on_event("MISC", "GET_FIRMWARE_VERSIONS", self.firmware_update)
        self.refresh_data()

    def setup_ui(self) -> Adw.Clamp:
        # Create the group to hold the info in a framed style
        self.group = Adw.PreferencesGroup(title="Device Information")

        # Create the refresh button
        refresh_btn = Gtk.Button(icon_name="view-refresh-symbolic")
        refresh_btn.set_tooltip_text("Refresh Device Information Module")
        refresh_btn.connect("clicked", self.refresh_data)
        refresh_btn.set_valign(Gtk.Align.CENTER)

        # Add the button to the group header
        self.group.set_header_suffix(refresh_btn)

        clamp = Adw.Clamp(maximum_size=400)
        clamp.set_child(self.group)

        self._setup_manufacturer_row()
        self._setup_model_row()
        self._setup_battery_row()
        self._setup_firmware_row()

        self._setup_callbacks()

        return clamp

    def refresh_data(self, sender=None):
        self.dbus.send("misc", "GET_MANUFACTURER")
        self.dbus.send("misc", "GET_MODEL")
        self.dbus.send("misc", "GET_BATTERY_STATE")
        self.dbus.send("misc", "GET_FIRMWARE_VERSIONS")

        if sender is not None:
            toast = Adw.Toast.new("Refreshing Device Status...")
            self.window.toast.add_toast(toast)

    def manufacturer_update(self, dir, flags, ptype, subf, pay):
        mfg = Manufacturer.parse(convert_list_payload(pay))
        GLib.idle_add(self.mfg_label.set_text, str(mfg))

    def model_update(self, dir, flags, ptype, subf, pay):
        mdl = Model.parse(convert_list_payload(pay))
        self.current_model_name = str(mdl)
        GLib.idle_add(self.model_label.set_text, self.current_model_name)

    @staticmethod
    def _format_battery_text(state: BatteryState, model_name: str) -> str:
        config = BATTERY_DISPLAY_CONFIG.get(model_name, BATTERY_DISPLAY_CONFIG["Default"])
        parts = []

        for field in config["display_fields"]:
            val = getattr(state, field)
            label = config["labels"].get(field, field)
            parts.append(f"{label}: {val}%")

        return " | ".join(parts) if parts else "No data"

    def battery_update(self, dir, flags, ptype, subf, pay):
        state = BatteryState.parse(convert_list_payload(pay))
        model_name = getattr(self, "current_model_name", "Default")        

        display = DeviceInfoModule._format_battery_text(state, model_name)
        GLib.idle_add(self.battery_label.set_text, display)

    def firmware_update(self, dir, flags, ptype, subf, pay):
        firmware = FirmwareVersion.parse(convert_list_payload(pay))
        GLib.idle_add(self.firmware_label.set_text, str(firmware))