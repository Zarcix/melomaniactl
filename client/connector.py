from collections import defaultdict
from concurrent.futures import ThreadPoolExecutor
from typing import Any, Callable

import dbus

BUS_NAME = "com.meloadapter.MeloControl"
OBJ_PATH = "/com/meloadapter/MeloControl"
IFACE = "com.meloadapter.MeloControl"

WORKER_COUNT = 4

type CommandCallback = Callable[[Any, Any, Any, Any, Any], None]

class MeloDBus:
    def __init__(self):
        self.bus = dbus.SessionBus()
        obj = self.bus.get_object(BUS_NAME, OBJ_PATH)
        self.iface = dbus.Interface(obj, dbus_interface=IFACE)

        self._events = defaultdict(set)
        self._executor = ThreadPoolExecutor(max_workers=WORKER_COUNT)

        self.bus.add_signal_receiver(
            self.recv,
            signal_name="CommandReceived",
            dbus_interface=IFACE,
            path=OBJ_PATH,
        )

    def on_event(self, feature: str, subfeature: str, callback_fn: CommandCallback):
        self._events[(feature.upper(), subfeature.upper())].add(callback_fn)

    def recv(self, direction: str, flags: str, ptype: str, feature: str, subfeature: str, payload: str):
        subscriber_list = self._events.get((feature.upper(), subfeature.upper()))
        if not subscriber_list:
            return

        for callback_fn in subscriber_list:
            self._executor.submit(callback_fn, direction, flags, ptype, subfeature, payload)

    def send(self, feature: str, subfeature: str, payload: str = ""):
        self.iface.SendCommand(feature, subfeature, payload)

    def shutdown(self):
        self._executor.shutdown(wait=True)
