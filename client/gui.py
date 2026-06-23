#!/usr/bin/env python3
"""Melomania — reactive GTK4/libadwaita client.

Talks to the MeloControl daemon purely over the DBus session bus: it calls the
``SendCommand`` method and subscribes to the ``CommandReceived`` signal. Every
incoming (RX) packet is routed by its subfeature name to the control that owns
it, which decodes the payload with the existing ``parsers`` package and updates
itself live. No packet/RFCOMM logic lives here — that all stays in the daemon.
"""
import os
import sys

# Allow `import parsers...` when run as `python client/gui.py` from anywhere.
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import gi

gi.require_version("Gtk", "4.0")
gi.require_version("Adw", "1")
from gi.repository import Adw, Gtk, GLib, Gio, Gdk  # noqa: E402

import dbus  # noqa: E402
import dbus.mainloop.glib  # noqa: E402

from parsers.mode.gaming_mode import GamingMode  # noqa: E402
from parsers.mode.proximity_mode import ProximityMode  # noqa: E402
from parsers.misc.side_tone import SideTone  # noqa: E402
from parsers.misc.loudness import Loudness  # noqa: E402
from parsers.misc.ambient_noise_mode import AmbientNoiseMode, AmbientNoiseCategory  # noqa: E402
from parsers.misc.language import Language  # noqa: E402
from parsers.misc.battery_state import BatteryState, ChargingState  # noqa: E402
from parsers.misc.manufacturer import Manufacturer  # noqa: E402
from parsers.misc.model import Model  # noqa: E402
from parsers.misc.api_level import APILevel  # noqa: E402
from parsers.misc.firmware_version import FirmwareVersion  # noqa: E402
from parsers.misc.variant import Variant  # noqa: E402
from parsers.codec.codecs import Codecs  # noqa: E402

BUS_NAME = "com.meloadapter.MeloControl"
OBJ_PATH = "/com/meloadapter/MeloControl"
IFACE = "com.meloadapter.MeloControl"

APP_CSS = """
.status-pill {
    padding: 3px 12px;
    border-radius: 999px;
    font-weight: bold;
    font-size: 0.85em;
}
.status-pill.on  { background: alpha(@success_color, 0.18); color: @success_color; }
.status-pill.off { background: alpha(@error_color,   0.18); color: @error_color;   }
.battery-row { padding: 4px 0; }
.battery-name { min-width: 56px; }
.battery-bar { min-height: 10px; }
.charging { color: @success_color; font-weight: bold; }
.log-view  { font-family: monospace; font-size: 0.85em; padding: 6px; }
.section-title { font-weight: bold; }
"""


def parse_payload(payload: str) -> list[int]:
    """Daemon emits the payload as comma-separated ints (or empty)."""
    payload = payload.strip()
    if not payload:
        return []
    out = []
    for chunk in payload.split(","):
        chunk = chunk.strip()
        if chunk:
            out.append(int(chunk))
    return out


def pretty(name: str) -> str:
    return name.replace("_", " ").title()


# --------------------------------------------------------------------------- #
# DBus bridge
# --------------------------------------------------------------------------- #
class MeloDBus:
    """Thin wrapper around the session bus.

    Uses watch_name_owner so connection state is reactive: it fires immediately
    with the current owner and again whenever the daemon comes or goes.
    """

    def __init__(self, on_signal, on_status):
        self._on_signal = on_signal
        self._on_status = on_status
        self.iface = None

        self.bus = dbus.SessionBus()
        self.bus.add_signal_receiver(
            self._signal,
            signal_name="CommandReceived",
            dbus_interface=IFACE,
            path=OBJ_PATH,
        )
        self.bus.watch_name_owner(BUS_NAME, self._owner_changed)

    def _owner_changed(self, owner):
        if owner:
            obj = self.bus.get_object(BUS_NAME, OBJ_PATH)
            self.iface = dbus.Interface(obj, IFACE)
        else:
            self.iface = None
        self._on_status(bool(owner))

    def _signal(self, direction, flags, ptype, feature, subfeature, payload):
        self._on_signal(
            str(direction), str(flags), str(ptype),
            str(feature), str(subfeature), str(payload),
        )

    def send(self, feature: str, subfeature: str, payload: str = "") -> bool:
        if self.iface is None:
            return False
        try:
            self.iface.SendCommand(feature, subfeature, payload)
            return True
        except dbus.DBusException:
            return False


# --------------------------------------------------------------------------- #
# Controls — each knows its (feature, subfeatures) and how to decode RX
# --------------------------------------------------------------------------- #
class Toggle:
    def __init__(self, send, title, feature, set_sub, get_sub, enum=None, subtitle=None):
        self._send = send
        self.feature = feature
        self.set_sub = set_sub
        self.get_sub = get_sub
        self.enum = enum
        self._suppress = False

        self.row = Adw.SwitchRow(title=title)
        if subtitle:
            self.row.set_subtitle(subtitle)
        self.row.connect("notify::active", self._toggled)

    def subfeatures(self):
        return [self.set_sub, self.get_sub]

    def _value(self, on):
        if self.enum is not None:
            return self.enum.ON.value if on else self.enum.OFF.value
        return 1 if on else 0

    def _toggled(self, row, _param):
        if self._suppress:
            return
        self._send(self.feature, self.set_sub, str(self._value(row.get_active())))

    def update(self, payload):
        ints = parse_payload(payload)
        if not ints:
            return
        self._suppress = True
        self.row.set_active(ints[0] != 0)
        self._suppress = False

    def query(self):
        self._send(self.feature, self.get_sub, "")


class Dropdown:
    def __init__(self, send, title, feature, set_sub, get_sub, enum):
        self._send = send
        self.feature = feature
        self.set_sub = set_sub
        self.get_sub = get_sub
        self.enum = enum
        self.members = list(enum)
        self._suppress = False

        model = Gtk.StringList()
        for m in self.members:
            model.append(pretty(m.name))
        self.row = Adw.ComboRow(title=title, model=model)
        self.row.connect("notify::selected", self._selected)

    def subfeatures(self):
        return [self.set_sub, self.get_sub]

    def _selected(self, row, _param):
        if self._suppress:
            return
        idx = row.get_selected()
        if 0 <= idx < len(self.members):
            self._send(self.feature, self.set_sub, str(self.members[idx].value))

    def update(self, payload):
        ints = parse_payload(payload)
        if not ints:
            return
        try:
            member = self.enum(ints[0])
        except ValueError:
            return
        self._suppress = True
        self.row.set_selected(self.members.index(member))
        self._suppress = False

    def query(self):
        self._send(self.feature, self.get_sub, "")


class AmbientSwitch:
    """Segmented Normal / ANC / Transparency selector via SWITCH_AMBIENT_NOISE_MODE.

    SWITCH takes a category index (see AmbientNoiseCategory). The device has no
    GET for the category, but it pushes a GET_AMBIENT_NOISE_MODE notification on
    every change carrying the active *detailed* mode; AmbientNoiseMode.category
    maps that back to the segment to highlight.
    """

    feature = "MISC"
    switch_sub = "SWITCH_AMBIENT_NOISE_MODE"
    get_sub = "GET_AMBIENT_NOISE_MODE"

    def __init__(self, send):
        self._send = send
        self._suppress = False
        self.categories = list(AmbientNoiseCategory)

        self.row = Adw.ActionRow(title="Ambient Sound")
        box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL)
        box.add_css_class("linked")
        box.set_valign(Gtk.Align.CENTER)

        self._buttons = []
        group = None
        for cat in self.categories:
            btn = Gtk.ToggleButton(label=pretty(cat.name))
            if group is None:
                group = btn
            else:
                btn.set_group(group)
            btn.connect("toggled", self._toggled, cat)
            box.append(btn)
            self._buttons.append(btn)
        self.row.add_suffix(box)

    def subfeatures(self):
        return [self.get_sub, self.switch_sub]

    def _toggled(self, btn, category):
        if self._suppress or not btn.get_active():
            return
        self._send(self.feature, self.switch_sub, str(category.value))

    def update(self, payload):
        ints = parse_payload(payload)
        if not ints:
            return
        try:
            category = AmbientNoiseMode(ints[0]).category
        except ValueError:
            return
        self._suppress = True
        self._buttons[self.categories.index(category)].set_active(True)
        self._suppress = False

    def query(self):
        self._send(self.feature, self.get_sub, "")


class Info:
    """Read-only value row decoded through a parser."""

    def __init__(self, send, title, feature, get_sub, parser):
        self._send = send
        self.feature = feature
        self.get_sub = get_sub
        self.parser = parser

        self.row = Adw.ActionRow(title=title)
        self._value = Gtk.Label(label="—")
        self._value.add_css_class("dim-label")
        self._value.set_selectable(True)
        self.row.add_suffix(self._value)

    def subfeatures(self):
        return [self.get_sub]

    def update(self, payload):
        ints = parse_payload(payload)
        if not ints:
            self._value.set_text("—")
            return
        try:
            value = self.parser.parse(ints)
        except Exception:
            value = ints
        if isinstance(value, list):
            text = ", ".join(str(v) for v in value)
        else:
            text = str(value)
        self._value.set_text(text or "—")

    def query(self):
        self._send(self.feature, self.get_sub, "")


class Battery:
    """Custom card: left / right / case level bars + charging indicators."""

    feature = "MISC"
    get_sub = "GET_BATTERY_STATE"

    def __init__(self, send):
        self._send = send

        self.widget = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=6)
        self.widget.add_css_class("card")

        inner = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=6)
        inner.set_margin_top(12)
        inner.set_margin_bottom(12)
        inner.set_margin_start(14)
        inner.set_margin_end(14)
        self.widget.append(inner)

        title = Gtk.Label(label="Battery", xalign=0)
        title.add_css_class("section-title")
        inner.append(title)

        self._bars = {}
        self._pct = {}
        self._chg = {}
        for key, label in (("left", "Left"), ("right", "Right"), ("case", "Case")):
            row = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=10)
            row.add_css_class("battery-row")

            name = Gtk.Label(label=label, xalign=0)
            name.add_css_class("battery-name")
            row.append(name)

            bar = Gtk.LevelBar(min_value=0, max_value=100)
            bar.set_hexpand(True)
            bar.set_valign(Gtk.Align.CENTER)
            bar.add_css_class("battery-bar")
            bar.add_offset_value("low", 20)
            bar.add_offset_value("high", 50)
            bar.add_offset_value("full", 100)
            row.append(bar)

            chg = Gtk.Label(label="")
            chg.add_css_class("charging")
            row.append(chg)

            pct = Gtk.Label(label="—", xalign=1)
            pct.set_width_chars(4)
            row.append(pct)

            inner.append(row)
            self._bars[key], self._pct[key], self._chg[key] = bar, pct, chg

    def subfeatures(self):
        return [self.get_sub]

    def _set(self, key, percent, charging):
        bar, pct, chg = self._bars[key], self._pct[key], self._chg[key]
        if 0 <= percent <= 100:
            bar.set_value(percent)
            pct.set_text(f"{percent}%")
        else:
            bar.set_value(0)
            pct.set_text("—")
        chg.set_text("⚡" if charging == ChargingState.CHARGING else "")

    def update(self, payload):
        state = BatteryState.parse(parse_payload(payload))
        if not isinstance(state, BatteryState):
            return
        self._set("left", state.left_percent, state.left_charging_state)
        self._set("right", state.right_percent, state.right_charging_state)
        self._set("case", state.case_percent, state.case_charging_state)

    def query(self):
        self._send(self.feature, self.get_sub, "")


# --------------------------------------------------------------------------- #
# Window
# --------------------------------------------------------------------------- #
class MeloWindow(Adw.ApplicationWindow):
    def __init__(self, app):
        super().__init__(application=app, title="Melomania")
        self.set_default_size(480, 760)

        self.controls = []
        self.registry = {}  # subfeature name -> [controls]

        self.toast = Adw.ToastOverlay()
        self.set_content(self.toast)

        toolbar = Adw.ToolbarView()
        self.toast.set_child(toolbar)

        header = Adw.HeaderBar()
        toolbar.add_top_bar(header)

        self.refresh_btn = Gtk.Button(icon_name="view-refresh-symbolic")
        self.refresh_btn.set_tooltip_text("Refresh all values")
        self.refresh_btn.connect("clicked", lambda _b: self.refresh())
        self.refresh_btn.set_sensitive(False)
        header.pack_start(self.refresh_btn)

        self.status_pill = Gtk.Label(label="Disconnected")
        self.status_pill.add_css_class("status-pill")
        self.status_pill.add_css_class("off")
        header.pack_end(self.status_pill)

        self.banner = Adw.Banner(
            title="Daemon not running — start the MeloControl daemon to connect.",
            revealed=True,
        )
        toolbar.add_top_bar(self.banner)

        scroller = Gtk.ScrolledWindow(hexpand=True, vexpand=True)
        toolbar.set_content(scroller)

        clamp = Adw.Clamp(maximum_size=560, margin_top=16, margin_bottom=16,
                          margin_start=12, margin_end=12)
        scroller.set_child(clamp)

        page = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=18)
        clamp.set_child(page)

        # Battery card
        self.battery = Battery(self.send)
        self._register(self.battery)
        page.append(self.battery.widget)

        # Modes
        page.append(self._group("Modes", None, [
            Toggle(self.send, "Gaming Mode", "MODE", "SET_GAMING_MODE", "GET_GAMING_MODE", GamingMode),
            Toggle(self.send, "Flight Mode", "MODE", "SET_FLIGHT_MODE", "GET_FLIGHT_MODE"),
            Toggle(self.send, "Mono Mode", "MODE", "SET_MONO_MODE", "GET_MONO_MODE"),
            Toggle(self.send, "Sleep Mode", "MODE", "SET_SLEEP_MODE", "GET_SLEEP_MODE"),
            Toggle(self.send, "Proximity Mode", "MODE", "SET_PROXIMITY_MODE", "GET_PROXIMITY_MODE", ProximityMode),
        ]))

        # Sound
        page.append(self._group("Sound", None, [
            Toggle(self.send, "Side Tone", "MISC", "SET_SIDE_TONE", "GET_SIDE_TONE", SideTone),
            Toggle(self.send, "Loudness", "MISC", "SET_LOUDNESS", "GET_LOUDNESS", Loudness),
            AmbientSwitch(self.send),
            Dropdown(self.send, "Noise Mode (detailed)", "MISC", "SET_AMBIENT_NOISE_MODE", "GET_AMBIENT_NOISE_MODE", AmbientNoiseMode),
            Dropdown(self.send, "Language", "MISC", "SET_LANGUAGE", "GET_LANGUAGE", Language),
            Info(self.send, "Current Codec", "CODEC", "GET_CURRENT_CODEC", Codecs),
        ]))

        # Device info
        page.append(self._group("Device", None, [
            Info(self.send, "Manufacturer", "MISC", "GET_MANUFACTURER", Manufacturer),
            Info(self.send, "Model", "MISC", "GET_MODEL", Model),
            Info(self.send, "Firmware", "MISC", "GET_FIRMWARE_VERSIONS", FirmwareVersion),
            Info(self.send, "API Level", "MISC", "GET_API_LEVEL", APILevel),
            Info(self.send, "Variant", "MISC", "GET_VARIANT", Variant),
        ]))

        # Activity log
        page.append(self._build_log())

        # DBus last, so callbacks can safely touch the widgets above.
        self.dbus = MeloDBus(self._on_signal, self._on_status)

    # -- construction helpers ------------------------------------------------ #
    def _group(self, title, description, controls):
        group = Adw.PreferencesGroup(title=title)
        if description:
            group.set_description(description)
        for ctrl in controls:
            self._register(ctrl)
            group.add(ctrl.row)
        return group

    def _register(self, ctrl):
        self.controls.append(ctrl)
        for sub in ctrl.subfeatures():
            self.registry.setdefault(sub, []).append(ctrl)

    def _build_log(self):
        expander = Gtk.Expander(label="Activity Log")
        expander.add_css_class("section-title")

        scroller = Gtk.ScrolledWindow(min_content_height=150, max_content_height=220)
        scroller.set_margin_top(6)
        self.log_buffer = Gtk.TextBuffer()
        view = Gtk.TextView(buffer=self.log_buffer, editable=False, cursor_visible=False,
                            monospace=True, wrap_mode=Gtk.WrapMode.WORD_CHAR)
        view.add_css_class("log-view")
        scroller.set_child(view)
        expander.set_child(scroller)
        return expander

    # -- runtime ------------------------------------------------------------- #
    def send(self, feature, subfeature, payload=""):
        ok = self.dbus.send(feature, subfeature, payload) if hasattr(self, "dbus") else False
        if subfeature.startswith("SET_"):
            self._log("TX", feature, subfeature, payload)
            if not ok:
                self.toast.add_toast(Adw.Toast(title="Not connected to daemon"))
        return ok

    def refresh(self):
        for ctrl in self.controls:
            ctrl.query()

    def _on_status(self, connected):
        self.refresh_btn.set_sensitive(connected)
        self.banner.set_revealed(not connected)
        self.status_pill.set_text("Connected" if connected else "Disconnected")
        self.status_pill.remove_css_class("on" if not connected else "off")
        self.status_pill.add_css_class("on" if connected else "off")
        if connected:
            # Give the daemon a beat to settle, then pull current state.
            GLib.timeout_add(150, lambda: (self.refresh(), False)[1])

    def _on_signal(self, direction, flags, ptype, feature, subfeature, payload):
        self._log("RX", feature, subfeature, payload)
        for ctrl in self.registry.get(subfeature, ()):  # reactive update
            try:
                ctrl.update(payload)
            except Exception as exc:  # never let a bad packet kill the UI
                self._log("ERR", feature, subfeature, str(exc))

    def _log(self, tag, feature, subfeature, payload):
        line = f"[{tag}] {feature}.{subfeature}"
        if payload:
            line += f"  {payload}"
        end = self.log_buffer.get_end_iter()
        self.log_buffer.insert(end, line + "\n")
        # Cap the buffer so it doesn't grow without bound.
        if self.log_buffer.get_line_count() > 500:
            start = self.log_buffer.get_start_iter()
            cut = self.log_buffer.get_iter_at_line(100)
            if isinstance(cut, tuple):  # GTK4 returns (ok, iter)
                cut = cut[1]
            self.log_buffer.delete(start, cut)


class MeloApp(Adw.Application):
    def __init__(self):
        super().__init__(application_id="com.meloadapter.MelomaniaGui",
                         flags=Gio.ApplicationFlags.DEFAULT_FLAGS)

    def do_activate(self):
        provider = Gtk.CssProvider()
        provider.load_from_data(APP_CSS)
        Gtk.StyleContext.add_provider_for_display(
            Gdk.Display.get_default(),
            provider,
            Gtk.STYLE_PROVIDER_PRIORITY_APPLICATION,
        )
        win = self.props.active_window or MeloWindow(self)
        win.present()


def main():
    dbus.mainloop.glib.DBusGMainLoop(set_as_default=True)
    app = MeloApp()
    app.run(sys.argv)


if __name__ == "__main__":
    main()
