from enum import Enum
from typing import Self

class ProximityMode(Enum):
    OFF = 0
    ON = 1

    @classmethod
    def parse(cls, payload: list[int]) -> Self:
        if len(payload) < 1:
            return None

        try:
            return cls(payload[0])
        except:
            return None

