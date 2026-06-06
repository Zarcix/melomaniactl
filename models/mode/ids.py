from enum import Enum
from typing import Self, Tuple

from .audio_mode import AudioMode
from .flight_mode import FlightMode
from .gaming_mode import GamingMode
from .mono_mode import MonoMode
from .proximity_mode import ProximityMode
from .sleep_mode import SleepMode

type PayloadParsers = Tuple[
    AudioMode,
    FlightMode,
    GamingMode,
    MonoMode,
    ProximityMode,
    SleepMode,
]

class ModeIds(Enum):
    SET_GAMING_MODE = 0
    GET_GAMING_MODE = 1

    SET_FLIGHT_MODE = 2
    GET_FLIGHT_MODE = 3

    GET_AUDIO_MODE = 5

    SET_PROXIMITY_MODE = 6
    GET_PROXIMITY_MODE = 7

    SET_MONO_MODE = 8
    GET_MONO_MODE = 9

    SET_SLEEP_MODE = 10
    GET_SLEEP_MODE = 11

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
            case self.SET_GAMING_MODE | self.GET_GAMING_MODE:
                return GamingMode
            case self.SET_FLIGHT_MODE | self.GET_FLIGHT_MODE:
                return FlightMode
            case self.SET_PROXIMITY_MODE | self.GET_PROXIMITY_MODE:
                return ProximityMode
            case self.SET_MONO_MODE | self.GET_MONO_MODE:
                return MonoMode
            case self.SET_SLEEP_MODE | self.GET_SLEEP_MODE:
                return SleepMode
            case self.GET_AUDIO_MODE:
                return AudioMode

        raise ValueError(f"Mode Payload Parser Not Found. Type={self.name}")
