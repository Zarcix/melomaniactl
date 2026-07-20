#!/usr/bin/env python3

import dbus
import dbus.mainloop.glib
import sys

# Adw Imports

import gi
gi.require_version("Gtk", "4.0")
gi.require_version("Adw", "1")

from gi.repository import Adw, Gtk

# Self Owned Modules

from connector import MeloDBus
import modules

class MeloWindow(Adw.ApplicationWindow):
    def __init__(self, app):
        super().__init__(application=app, title="MeloControl")
        self.set_default_size(480, 760)
        self.dbus = MeloDBus()

        self.toast = Adw.ToastOverlay()
        self.set_content(self.toast)

        toolbar = Adw.ToolbarView()
        self.toast.set_child(toolbar)

        header = Adw.HeaderBar()
        toolbar.add_top_bar(header)

        reload_btn = Gtk.Button(icon_name="view-refresh-symbolic")
        reload_btn.set_tooltip_text("Refresh All Modules")
        reload_btn.connect("clicked", self.refresh_all)
        header.pack_start(reload_btn)

        self.main_container = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=12)
        toolbar.set_content(self.main_container)

        self.modules = []
        for module_cls in modules.get_all_modules():
            self.modules.append(module_cls(self))

    def refresh_all(self, _):
        for module in self.modules:
            module.refresh_data()

        toast = Adw.Toast.new("Refreshing all modules...")
        self.toast.add_toast(toast)

class MeloApp(Adw.Application):
    def do_activate(self):
        win = MeloWindow(self)
        win.present()

def main():
    dbus.mainloop.glib.DBusGMainLoop(set_as_default=True)
    app = MeloApp()
    app.run(sys.argv)

if __name__ == "__main__":
    main()
