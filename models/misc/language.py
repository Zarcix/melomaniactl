from enum import Enum
from typing import Self

class Language(Enum):
    TONES = 0
    ENGLISH = 1
    GERMAN = 2
    SPANISH = 3
    ITALIAN = 4
    JAPANESE = 5
    KOREAN = 6
    CANTONESE = 7
    MANDARIN = 8
    FRENCH = 9
    CELEBRITY = 10
    OFF = 255

    @classmethod
    def parse(cls, payload: list[int]) -> Self | list[int]:
        if len(payload) != 1:
            print(f"Language Parse Failed: Invalid Payload Size")
            return payload
        return cls(payload[0])
