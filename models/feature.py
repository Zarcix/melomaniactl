from enum import Enum
from typing import Type

from .misc import Misc
from .mode import Mode
from .codec import Codec
from .gesture import Gesture

class Feature(Enum):
    # The tuple is passed to __new__
    MISC = (0, Misc)
    MODE = (1, Mode)
    CODEC = (2, Codec)
    GESTURE = (3, Gesture)

    def __new__(cls, value: int, subfeature_cls: Type):
        obj = object.__new__(cls)
        # This tells the Enum that ONLY the int is the .value
        obj._value_ = value 
        # This attaches the extra data as an attribute
        obj.subfeature_cls = subfeature_cls
        return obj

    @classmethod
    def from_name(cls, name: str) -> 'Feature':
        return cls[name.upper()]