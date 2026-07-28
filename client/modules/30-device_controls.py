from gi.repository import Gtk, Adw, GLib

from parsers.misc.loudness import Loudness
from parsers.misc.side_tone import SideTone
from parsers.mode.gaming_mode import GamingMode
from parsers.mode.proximity_mode import ProximityMode

from parsers.misc.auto_power_down_timeout import AutoPowerDownTimeout
from parsers.misc.language import Language

from .base import BaseModule

from util import convert_list_payload

class DeviceControlsModule(BaseModule):
    def _setup_loudness_row(self):
        self.loudness_row = Adw.ActionRow(title="Loudness")
        self.loudness_switch = Gtk.Switch()
        self.loudness_switch.set_valign(Gtk.Align.CENTER)
        self.loudness_switch.connect("state-set", self.loudness_set)
        self.loudness_row.add_suffix(self.loudness_switch)
        self.group.add(self.loudness_row)

    def _setup_sidetone_row(self):
        self.sidetone_row = Adw.ActionRow(title="Side Tone")
        self.sidetone_switch = Gtk.Switch()
        self.sidetone_switch.set_valign(Gtk.Align.CENTER)
        self.sidetone_switch.connect("state-set", self.sidetone_set)
        self.sidetone_row.add_suffix(self.sidetone_switch)
        self.group.add(self.sidetone_row)

    def _setup_proximity_row(self):
        self.proximity_row = Adw.ActionRow(title="Proximity Mode")
        self.proximity_switch = Gtk.Switch()
        self.proximity_switch.set_valign(Gtk.Align.CENTER)
        self.proximity_switch.connect("state-set", self.proximity_set)
        self.proximity_row.add_suffix(self.proximity_switch)
        self.group.add(self.proximity_row)

    def _setup_gaming_row(self):
        self.gaming_row = Adw.ActionRow(title="Gaming Mode")
        self.gaming_switch = Gtk.Switch()
        self.gaming_switch.set_valign(Gtk.Align.CENTER)
        self.gaming_switch.connect("state-set", self.gaming_set)
        self.gaming_row.add_suffix(self.gaming_switch)
        self.group.add(self.gaming_row)

    def _setup_language_row(self):
        self.language_row = Adw.ActionRow(title="Language")

        # Include OFF/255 if needed, or map all standard members:
        language_names = [lang.name.replace("_", " ").title() for lang in Language]
        self.language_model = Gtk.StringList.new(language_names)
        self.language_dropdown = Gtk.DropDown.new(self.language_model, None)
        self.language_dropdown.set_valign(Gtk.Align.CENTER)
        self.language_dropdown.connect("notify::selected", self.language_set)
        
        self.language_row.add_suffix(self.language_dropdown)
        self.group.add(self.language_row)

    def _setup_callbacks(self):
        self.dbus.on_event("MISC", "GET_LOUDNESS", self.loudness_update)
        self.dbus.on_event("MISC", "GET_SIDE_TONE", self.sidetone_update)

        self.dbus.on_event("MISC", "GET_LANGUAGE", self.language_update)

        self.dbus.on_event("MODE", "GET_PROXIMITY_MODE", self.proximity_update)
        self.dbus.on_event("MODE", "GET_GAMING_MODE", self.gaming_update)

        self.refresh_data()

    def setup_ui(self):
        # Create the group to hold the info in a framed style
        self.group = Adw.PreferencesGroup(title="Device Controls")

        # Create the refresh button
        refresh_btn = Gtk.ToggleButton(icon_name="view-refresh-symbolic")
        refresh_btn.set_tooltip_text("Refresh Device Controls")
        refresh_btn.connect("clicked", self.refresh_data)
        refresh_btn.set_valign(Gtk.Align.CENTER)

        # Add the button to the group header
        self.group.set_header_suffix(refresh_btn)

        self._setup_loudness_row()
        self._setup_sidetone_row()

        self._setup_proximity_row()
        self._setup_gaming_row()

        self._setup_language_row()

        self._setup_callbacks()

        clamp = Adw.Clamp(maximum_size=400)
        clamp.set_child(self.group)

        return clamp

    def refresh_data(self, sender=None):
        self.dbus.send("MISC", "GET_LOUDNESS")
        self.dbus.send("MISC", "GET_SIDE_TONE")

        self.dbus.send("MISC", "GET_AUTO_POWER_DOWN_TIMEOUT")
        self.dbus.send("MISC", "GET_LANGUAGE")

        self.dbus.send("MODE", "GET_PROXIMITY_MODE")
        self.dbus.send("MODE", "GET_GAMING_MODE")

        if sender is not None:
            toast = Adw.Toast.new("Refreshing Device Controls...")
            self.window.toast.add_toast(toast)

    def loudness_update(self, dir, flags, ptype, subf, pay):
        loudness = Loudness.parse(convert_list_payload(pay))
        loudness_active = loudness == Loudness.ON
        GLib.idle_add(self.loudness_switch.set_active, loudness_active)

    def loudness_set(self, switch, state):
        val = 1 if state else 0
        self.dbus.send("MISC", "SET_LOUDNESS", str(val))

    def sidetone_update(self, dir, flags, ptype, subf, pay):
        sidetone = SideTone.parse(convert_list_payload(pay))
        active = sidetone == SideTone.ON
        GLib.idle_add(self.sidetone_switch.set_active, active)

    def sidetone_set(self, switch, state):
        val = 1 if state else 0
        self.dbus.send("MISC", "SET_SIDE_TONE", str(val))

    def proximity_update(self, dir, flags, ptype, subf, pay):
        proximity_mode = ProximityMode.parse(convert_list_payload(pay))
        active = proximity_mode == ProximityMode.ON
        GLib.idle_add(self.proximity_switch.set_active, active)

    def proximity_set(self, switch, state):
        val = 1 if state else 0
        self.dbus.send("MODE", "SET_PROXIMITY_MODE", str(val))

    def gaming_update(self, dir, flags, ptype, subf, pay):
        gaming_mode = GamingMode.parse(convert_list_payload(pay))
        active = gaming_mode == GamingMode.ON
        GLib.idle_add(self.gaming_switch.set_active, active)

    def gaming_set(self, switch, state):
        val = 1 if state else 0
        self.dbus.send("MODE", "SET_GAMING_MODE", str(val))

    def language_update(self, dir, flags, ptype, subf, pay):
        lang = Language.parse(convert_list_payload(pay))
        languages = list(Language)

        try:
            index = languages.index(lang)
            GLib.idle_add(self.language_dropdown.set_selected, index)
        except ValueError:
            GLib.idle_add(self.language_dropdown.set_selected, pay)

    def language_set(self, dropdown, param):
        index = dropdown.get_selected()
        languages = list(Language)
        if 0 <= index < len(languages):
            lang = languages[index]
            self.dbus.send("MISC", "SET_LANGUAGE", str(lang.value))