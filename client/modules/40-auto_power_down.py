from gi.repository import Gtk, Adw, GLib

from parsers.misc.auto_power_down_timeout import AutoPowerDownTimeout

from .base import BaseModule

from util import convert_list_payload

class AutoPowerDownModule(BaseModule):
    def _setup_autopowerdown_row(self):
        row = Adw.PreferencesRow()
        row.set_selectable(False)
        row.set_activatable(False)

        box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=12)
        box.set_halign(Gtk.Align.CENTER)
        box.set_valign(Gtk.Align.CENTER)
        box.set_margin_top(18)
        box.set_margin_bottom(18)
        box.set_margin_start(18)
        box.set_margin_end(18)

        self.apd_hour_spin = Gtk.SpinButton.new_with_range(0, 255, 1)
        self.apd_minute_spin = Gtk.SpinButton.new_with_range(0, 59, 1)
        self.apd_second_spin = Gtk.SpinButton.new_with_range(0, 59, 1)

        for spin in (self.apd_hour_spin, self.apd_minute_spin, self.apd_second_spin):
            spin.set_valign(Gtk.Align.CENTER)
            spin.set_numeric(True)
            spin.set_width_chars(3)
            spin.connect("value-changed", self.autopowerdown_set)

        colon1 = Gtk.Label(label=":")
        colon2 = Gtk.Label(label=":")
        colon1.set_valign(Gtk.Align.CENTER)
        colon2.set_valign(Gtk.Align.CENTER)

        box.append(self.apd_hour_spin)
        box.append(colon1)
        box.append(self.apd_minute_spin)
        box.append(colon2)
        box.append(self.apd_second_spin)

        row.set_child(box)
        self.group.add(row)

    def _setup_callbacks(self):
        self.dbus.on_event("MISC", "GET_AUTO_POWER_DOWN_TIMEOUT", self.autopowerdown_update)

        self.refresh_data()

    def setup_ui(self):
        # Create the group to hold the info in a framed style
        self.group = Adw.PreferencesGroup(title="Auto Power Down Controls")

        # Create the refresh button
        refresh_btn = Gtk.ToggleButton(icon_name="view-refresh-symbolic")
        refresh_btn.set_tooltip_text("Refresh Device Controls")
        refresh_btn.connect("clicked", self.refresh_data)
        refresh_btn.set_valign(Gtk.Align.CENTER)

        # Add the button to the group header
        self.group.set_header_suffix(refresh_btn)

        self._setup_autopowerdown_row()

        self._setup_callbacks()

        clamp = Adw.Clamp(maximum_size=400)
        clamp.set_child(self.group)

        return clamp

    def refresh_data(self, sender=None):
        self.dbus.send("MISC", "GET_AUTO_POWER_DOWN_TIMEOUT")

        if sender is not None:
            toast = Adw.Toast.new("Refreshing Auto Power Down...")
            self.window.toast.add_toast(toast)

    def autopowerdown_update(self, dir, flags, ptype, subf, pay):
        apd = AutoPowerDownTimeout.parse(convert_list_payload(pay))
        GLib.idle_add(self.apd_hour_spin.set_value, apd.hour)
        GLib.idle_add(self.apd_minute_spin.set_value, apd.minute)
        GLib.idle_add(self.apd_second_spin.set_value, apd.second)

    def autopowerdown_set(self, spin):
        h = int(self.apd_hour_spin.get_value())
        m = int(self.apd_minute_spin.get_value())
        s = int(self.apd_second_spin.get_value())
        payload_str = f"{h} {m} {s}"
        self.dbus.send("MISC", "SET_AUTO_POWER_DOWN_TIMEOUT", payload_str)
