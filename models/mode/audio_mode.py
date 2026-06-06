from enum import Enum
from typing import Self

class AudioMode(Enum):
    @classmethod
    def parse(cls, payload: list[int]) -> Self | list[int]:
        raise NotImplementedError(f"Payload={payload}")
