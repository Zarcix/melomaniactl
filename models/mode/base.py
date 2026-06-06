from enum import Enum
from typing import Self

from .gaming_mode import GamingMode
from .proximity_mode import ProximityMode

type PayloadParsers = GamingMode | ProximityMode

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
            case self.SET_PROXIMITY_MODE | self.GET_PROXIMITY_MODE:
                return ProximityMode
        return None