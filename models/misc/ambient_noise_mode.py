from enum import Enum
from typing import Self

class AmbientNoiseMode(Enum):
    OFF = 0
    ANC_HIGH = 1
    ANC_MED = 3
    ANC_LOW = 5

    ANC_HIGH_OFF = 7
    ANC_MED_OFF = 8
    ANC_LOW_OFF = 9

    TRANSPARENCY_LOW = 2
    TRANSPARENCY_HIGH = 4
    TRANSPARENCY_VOICE_FOCUS = 6

    @classmethod
    def parse(cls, payload: list[int]) -> Self | list[int]:
        if len(payload) != 1:
            print(f"Ambient Noise Mode Parse Failed: Invalid Payload Size")
            return payload
        return cls(payload[0])
