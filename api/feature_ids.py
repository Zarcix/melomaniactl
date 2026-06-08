from enum import Enum
from typing import Type

from .features import (
    CodecIds,
    GestureIds,
    ModeIds,
    MiscIds
)

class FeatureIds(Enum):
    # The tuple is passed to __new__
    MISC = (0, MiscIds)
    MODE = (1, ModeIds)
    CODEC = (2, CodecIds)
    GESTURE = (3, GestureIds)

    def __new__(cls, value: int, subfeature_cls: Type):
        obj = object.__new__(cls)
        # This tells the Enum that ONLY the int is the .value
        obj._value_ = value 
        # This attaches the extra data as an attribute
        obj.subfeature_cls = subfeature_cls
        return obj

    @classmethod
    def from_name(cls, name: str) -> FeatureIds:
        return cls[name.upper()]