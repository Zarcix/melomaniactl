from enum import Enum
from typing import Self

class GamingMode(Enum):
    OFF = 0
    ON = 1

    @classmethod
    def parse(cls, payload: list[int]) -> Self | list[int]:
        if len(payload) != 1:
            return payload

        try:
            return cls(payload[0])
        except:
            return payload
