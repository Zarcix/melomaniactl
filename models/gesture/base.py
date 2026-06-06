from enum import Enum
from typing import Self

from .gesture import Gesture

class GestureIds(Enum):
    GET_SUPPORTED_GESTURE_CONTROLS = 0

    GET_GESTURE_CONTROLS_ON_OFF = 1
    SET_GESTURE_CONTROLS_ON_OFF = 2

    SET_GESTURE_CONTROL_ON_OFF = 3

    @classmethod
    def from_name(cls, name: str) -> Self:
        try:
            return cls[name.upper()]
        except KeyError:
            # Handle the case where the name doesn't exist
            raise ValueError(f"{name} is not a valid {cls.__name__}")

    @property
    def payload_parser(self) -> Gesture:
        return Gesture
