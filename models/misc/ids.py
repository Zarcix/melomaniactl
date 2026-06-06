from enum import Enum
from typing import Self, Tuple

from .manufacturer import Manufacturer
from .language import Language

type PayloadParsers = Tuple[
    Manufacturer,
    Language,
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
        pass