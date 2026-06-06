from enum import Enum
from typing import Self

class AudioMode(Enum):
    @classmethod
    def parse(cls, payload: list[int]) -> Self | list[int]:
        print(f"Audio Mode Parsing: Unimplemented! Payload={payload}")
        return payload
