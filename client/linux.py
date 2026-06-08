import dbus
import dbus.mainloop.glib
import curses
import queue
import threading

from gi.repository import GLib

class MeloClient:
    def __init__(self):
        bus = dbus.SessionBus()

        bus.add_signal_receiver(
            self._on_signal,
            signal_name="CommandReceived",
            dbus_interface="com.meloadapter.MeloControl",
            path="/com/meloadapter/MeloControl",
        )

        obj = bus.get_object(
            "com.meloadapter.MeloControl",
            "/com/meloadapter/MeloControl",
        )

        self.iface = dbus.Interface(
            obj,
            dbus_interface="com.meloadapter.MeloControl",
        )

    def set_signal_callback(self, cb):
        self.signal_callback = cb

    def _on_signal(self, direction, flags, packet_type, feature, subfeature, payload):
        if self.signal_callback:
            self.signal_callback(
                direction, flags, packet_type,
                feature, subfeature, payload
            )

    def send_command(self, feature, subfeature, payload=""):
        self.iface.SendCommand(feature, subfeature, payload)

class CursesUI:
    def __init__(self, client: MeloClient):
        self.client = client
        self.running = True

        self.msg_queue = queue.Queue()

    def push_msg(self, msg: str):
        self.msg_queue.put(msg)

    def _draw(self, stdscr, log_lines, input_buf):
        stdscr.clear()
        h, w = stdscr.getmaxyx()

        # log window (all but bottom line)
        max_log = h - 2
        visible = log_lines[-max_log:]

        for i, line in enumerate(visible):
            stdscr.addnstr(i, 0, line, w - 1)

        # input bar
        stdscr.addnstr(h - 1, 0, ">>> " + input_buf, w - 1)

        stdscr.refresh()

    def _handle_command(self, cmd: str):
        parts = cmd.strip().split()

        if not parts:
            return

        if parts[0] in ("q", "quit", "exit"):
            self.running = False
            GLib.MainLoop().quit()
            return

        if parts[0] == "send":
            if len(parts) < 3:
                self.push_msg("[ERR] usage: send <feature> <subfeature> [payload]")
                return

            feature = parts[1]
            subfeature = parts[2]
            payload = " ".join(parts[3:]) if len(parts) > 3 else ""

            self.client.send_command(feature, subfeature, payload)
            self.push_msg(f"[TX] {feature}.{subfeature} {payload}")

        else:
            self.push_msg(f"[ERR] unknown command: {parts[0]}")

    def run(self, stdscr):
        curses.curs_set(1)
        stdscr.nodelay(True)
        stdscr.timeout(100)

        log_lines = []
        input_buf = ""

        while self.running:
            # flush incoming DBus messages
            while not self.msg_queue.empty():
                log_lines.append(self.msg_queue.get())

            try:
                key = stdscr.getch()

                if key == -1:
                    pass

                elif key in (10, 13):  # Enter
                    self._handle_command(input_buf)
                    input_buf = ""

                elif key in (127, curses.KEY_BACKSPACE):
                    input_buf = input_buf[:-1]

                elif key == 27:  # ESC
                    self.running = False
                    GLib.MainLoop().quit()
                    break

                elif 32 <= key <= 126:
                    input_buf += chr(key)

            except Exception as e:
                log_lines.append(f"[ERR] {e}")

            self._draw(stdscr, log_lines, input_buf)

        curses.endwin()

    def start(self):
        curses.wrapper(self.run)

def main():
    dbus.mainloop.glib.DBusGMainLoop(set_as_default=True)

    client = MeloClient()
    ui = CursesUI(client)

    def on_signal(direction, flags, packet_type, feature, subfeature, payload):
        ui.push_msg(
            f"[RX] {feature}.{subfeature} {payload}"
        )

    client.set_signal_callback(on_signal)

    threading.Thread(target=lambda: GLib.MainLoop().run(), daemon=True).start()

    ui.start()

if __name__ == "__main__":
    main()