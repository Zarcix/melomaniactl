from enum import Enum
from typing import Self

class Loudness(Enum):
    OFF = 0
    ON = 1

    @classmethod
    def parse(cls, payload: list[int]) -> Self | list[int]:
        if len(payload) != 1:
            print(f"Ambient Noise Mode Parse Failed: Invalid Payload Size")
            return payload
        return cls(*payload)
