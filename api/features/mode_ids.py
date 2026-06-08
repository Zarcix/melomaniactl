from enum import Enum
from typing import Self

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
