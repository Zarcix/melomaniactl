import time

from gi.repository import Gtk, Adw, GLib

from parsers.misc.ambient_noise_mode import AmbientNoiseMode, AmbientNoiseCategory
from parsers.misc.ambient_noise_toggle_option import AmbientNoiseToggleOption

from .base import BaseModule

from util import convert_list_payload

class AmbientNoiseControlModule(BaseModule):
    def __init__(self, window):
        self._current_mode = None
        self._toggle_options = None
        self._loading_options = False
        super().__init__(window)

    def _setup_anc_row(self):
        self.anc_mode = Adw.ActionRow(title="Operating Mode")

        box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=0)
        box.set_valign(Gtk.Align.CENTER)
        box.add_css_class("linked")

        self.btn_off = Gtk.ToggleButton(label="Off")
        self.btn_anc = Gtk.ToggleButton(label="ANC")
        self.btn_transparency = Gtk.ToggleButton(label="Transparency")

        self.btn_off.connect("clicked", lambda b: self._handle_mode_button_click(0, AmbientNoiseCategory.NORMAL))
        self.btn_anc.connect("clicked", lambda b: self._handle_mode_button_click(1, AmbientNoiseCategory.ANC))
        self.btn_transparency.connect("clicked", lambda b: self._handle_mode_button_click(2, AmbientNoiseCategory.TRANSPARENCY))

        box.append(self.btn_off)
        box.append(self.btn_anc)
        box.append(self.btn_transparency)

        self.anc_mode.add_suffix(box)
        self.group.add(self.anc_mode)

    def _handle_mode_button_click(self, mode_val: int, category: AmbientNoiseCategory):
        if self._current_mode and self._current_mode.category == category:
            self._show_level_dialog(category)
            return

        self.anc_switch(mode_val)

    def _show_level_dialog(self, category: AmbientNoiseCategory):
        dialog = Adw.AlertDialog.new("Select Level", None)

        match category:
            case AmbientNoiseCategory.NORMAL:
                return
            case AmbientNoiseCategory.ANC:
                levels = (
                    AmbientNoiseMode.ANC_HIGH,
                    AmbientNoiseMode.ANC_MED,
                    AmbientNoiseMode.ANC_LOW
                )
            case AmbientNoiseCategory.TRANSPARENCY:
                levels = (
                    AmbientNoiseMode.TRANSPARENCY_LOW,
                    AmbientNoiseMode.TRANSPARENCY_HIGH,
                    AmbientNoiseMode.TRANSPARENCY_VOICE_FOCUS
                )

        for mode in levels:
            dialog.add_response(str(mode.value), str(mode))

        dialog.add_response("cancel", "Cancel")
        dialog.set_close_response("cancel")

        def on_response(dlg, response):
            res = dlg.choose_finish(response)
            if res != "cancel":
                self.anc_set(int(res))

        dialog.choose(self.window, None, on_response)

    def _setup_anc_options_row(self):
        row = Adw.ActionRow(title="ANC Options")
        
        box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=6)
        box.set_valign(Gtk.Align.CENTER)

        self.tgl_normal = Gtk.ToggleButton(label="Normal")
        self.tgl_anc = Gtk.ToggleButton(label="ANC")
        self.tgl_transparency = Gtk.ToggleButton(label="Transparency")

        self.tgl_normal.connect("toggled", lambda b: self.anc_options_set())
        self.tgl_anc.connect("toggled", lambda b: self.anc_options_set())
        self.tgl_transparency.connect("toggled", lambda b: self.anc_options_set())

        box.append(self.tgl_normal)
        box.append(self.tgl_anc)
        box.append(self.tgl_transparency)

        row.add_suffix(box)
        self.group.add(row)

    def _setup_callbacks(self):
        self.dbus.on_event("MISC", "GET_AMBIENT_NOISE_MODE", self.anc_update)
        self.dbus.on_event("MISC", "GET_AMBIENT_NOISE_TOGGLE_OPTIONS", self.anc_options_update)

        self.refresh_data()

    def setup_ui(self):
        self.group = Adw.PreferencesGroup(title="Ambient Noise Controls")

        refresh_btn = Gtk.ToggleButton(icon_name="view-refresh-symbolic")
        refresh_btn.set_tooltip_text("Refresh Device Controls")
        refresh_btn.connect("clicked", self.refresh_data)
        refresh_btn.set_valign(Gtk.Align.CENTER)

        self.group.set_header_suffix(refresh_btn)

        self._setup_anc_row()
        self._setup_anc_options_row()

        self._setup_callbacks()

        clamp = Adw.Clamp(maximum_size=400)
        clamp.set_child(self.group)

        return clamp

    def refresh_data(self, sender=None):
        self.dbus.send("MISC", "GET_AMBIENT_NOISE_MODE")
        self.dbus.send("MISC", "GET_AMBIENT_NOISE_TOGGLE_OPTIONS")

        if sender is not None:
            toast = Adw.Toast.new("Refreshing ANC Controls...")
            self.window.toast.add_toast(toast)

    def anc_update(self, dir, flags, ptype, subf, pay):
        parsed = AmbientNoiseMode.parse(convert_list_payload(pay))
        if isinstance(parsed, list):
            return

        def update_ui():
            self._current_mode = parsed

            self.btn_off.set_active(False)
            self.btn_anc.set_active(False)
            self.btn_transparency.set_active(False)

            match self._current_mode.category:
                case AmbientNoiseCategory.NORMAL:
                    self.btn_off.set_active(True)
                case AmbientNoiseCategory.ANC:
                    self.btn_anc.set_active(True)
                case AmbientNoiseCategory.TRANSPARENCY:
                    self.btn_transparency.set_active(True)

            self.anc_mode.set_subtitle(f"{self._current_mode.name}")

        GLib.idle_add(update_ui)

    def anc_options_update(self, dir, flags, ptype, subf, pay):
        parsed = AmbientNoiseToggleOption.parse(convert_list_payload(pay))
        if isinstance(parsed, list):
            return

        def update_ui():
            self._loading_options = True
            self._toggle_options = parsed
            
            self.tgl_normal.set_active(bool(parsed.normal_mode))
            self.tgl_anc.set_active(bool(parsed.noise_cancel))
            self.tgl_transparency.set_active(bool(parsed.transparency))

            self._loading_options = False

        GLib.idle_add(update_ui)

    def anc_switch(self, mode_val: int):
        self.dbus.send("MISC", "SWITCH_AMBIENT_NOISE_MODE", str(mode_val))
        GLib.timeout_add_seconds(2, lambda: (self.refresh_data(), False)[1])

    def anc_set(self, mode_val: int):
        self.dbus.send("MISC", "SET_AMBIENT_NOISE_MODE", str(mode_val))
        GLib.timeout_add_seconds(2, lambda: (self.refresh_data(), False)[1])

    def anc_options_set(self):
        if self._loading_options or not hasattr(self, "tgl_normal") or not self._toggle_options:
            return

        normal_val = 1 if self.tgl_normal.get_active() else 0
        anc_val = 1 if self.tgl_anc.get_active() else 0
        trans_val = 1 if self.tgl_transparency.get_active() else 0

        payload = f"{normal_val} {anc_val} {trans_val}"
        self.dbus.send("MISC", "SET_AMBIENT_NOISE_TOGGLE_OPTIONS", payload)