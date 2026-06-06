from enum import Enum
from typing import Self

from .codecs import Codecs

class CodecIds(Enum):
    SET_ENABLED_CODECS = 0
    GET_ENABLED_CODECS = 1

    GET_AVAILABLE_CODECS = 2

    GET_CURRENT_CODEC = 3

    @classmethod
    def from_name(cls, name: str) -> Self:
        try:
            return cls[name.upper()]
        except KeyError:
            # Handle the case where the name doesn't exist
            raise ValueError(f"{name} is not a valid {cls.__name__}")

    @property
    def payload_parser(self) -> Codecs:
        return Codecs