from enum import Enum
from typing import Self, Tuple

from .manufacturer import Manufacturer
from .model import Model
from .api_level import APILevel
from .battery_state import BatteryState
from .language import Language
from .auto_power_down_timeout import AutoPowerDownTimeout
from .ambient_noise_mode import AmbientNoiseMode
from .ambient_noise_toggle_option import AmbientNoiseToggleOption
from .loudness import Loudness
from .device import ConnectedDevice
from .side_tone import SideTone

class GenericParser:
    def parse(payload: list[int]) -> list[int]:
        return payload

type PayloadParsers = Tuple[
    GenericParser,
    Manufacturer,
    Model,
    APILevel,
    BatteryState,
    # Firmware Versions
    # Bluetooth Addresses
    Language,
    AutoPowerDownTimeout,
    # Left Right Balance
    # Headphones Alert
    AmbientNoiseMode,
    # Variant
    AmbientNoiseToggleOption,
    Loudness,
    ConnectedDevice,
    SideTone,
]

class MiscIds(Enum):
    GET_MANUFACTURER = 0
    GET_MODEL = 1
    GET_API_LEVEL = 2
    GET_BATTERY_STATE = 3
    GET_FIRMWARE_VERSIONS = 4
    GET_BLUETOOTH_ADDRESSES = 5

    GET_LANGUAGE = 6
    SET_LANGUAGE = 7

    SET_AUTO_POWER_DOWN_TIMEOUT = 8
    GET_AUTO_POWER_DOWN_TIMEOUT = 9

    SET_LEFT_RIGHT_BALANCE = 10
    GET_LEFT_RIGHT_BALANCE = 11

    SET_FIND_HEADPHONES_ALERT = 12
    GET_FIND_HEADPHONES_ALERT = 13

    SWITCH_AMBIENT_NOISE_MODE = 14
    SET_AMBIENT_NOISE_MODE = 15
    GET_AMBIENT_NOISE_MODE = 16

    GET_VARIANT = 17

    SET_AMBIENT_NOISE_TOGGLE_OPTIONS = 18
    GET_AMBIENT_NOISE_TOGGLE_OPTIONS = 19

    SET_LOUDNESS = 20
    GET_LOUDNESS = 21

    GET_DEVICES = 22
    CONNECT_DEVICE = 23
    DISCONNECT_DEVICE = 24

    SET_SIDE_TONE = 25
    GET_SIDE_TONE = 26

    @classmethod
    def from_name(cls, name: str) -> Self:
        try:
            return cls[name.upper()]
        except KeyError:
            # Handle the case where the name doesn't exist
            raise ValueError(f"{name} is not a valid {cls.__name__}")

    @property
    def payload_parser(self) -> PayloadParsers:
        match (self):
            case self.GET_MANUFACTURER:
                return Manufacturer
            case self.GET_MODEL:
                return Model
            case self.GET_API_LEVEL:
                return APILevel
            case self.GET_BATTERY_STATE:
                return BatteryState
            case self.GET_LANGUAGE | self.SET_LANGUAGE:
                return Language
            case self.GET_AUTO_POWER_DOWN_TIMEOUT | self.SET_AUTO_POWER_DOWN_TIMEOUT:
                return AutoPowerDownTimeout
            case self.SET_LEFT_RIGHT_BALANCE | self.GET_LEFT_RIGHT_BALANCE:
                return GenericParser
            case self.SET_FIND_HEADPHONES_ALERT | self.GET_FIND_HEADPHONES_ALERT:
                return GenericParser
            case self.SWITCH_AMBIENT_NOISE_MODE | self.SET_AMBIENT_NOISE_MODE | self.GET_AMBIENT_NOISE_MODE:
                return AmbientNoiseMode
            case self.GET_VARIANT:
                return GenericParser
            case self.SET_AMBIENT_NOISE_TOGGLE_OPTIONS | self.GET_AMBIENT_NOISE_TOGGLE_OPTIONS:
                return AmbientNoiseToggleOption
            case self.SET_LOUDNESS | self.GET_LOUDNESS:
                return Loudness
            case self.GET_DEVICES | self.CONNECT_DEVICE | self.DISCONNECT_DEVICE:
                return ConnectedDevice
            case self.SET_SIDE_TONE | self.GET_SIDE_TONE:
                return SideTone