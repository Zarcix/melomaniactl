from abc import ABC, abstractmethod
from gi.repository import Adw

class BaseModule(ABC):
    def __init__(self, window):
        self.window = window
        self.dbus = window.dbus
        self.box = self.setup_ui()
        if self.box:
            self.window.main_container.append(self.box)

    @abstractmethod
    def refresh_data(self, sender=None):
        pass

    @abstractmethod
    def setup_ui(self) -> Adw.Clamp:
        pass