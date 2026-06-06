from enum import Enum
from typing import Self

class SleepMode(Enum):
    @classmethod
    def parse(cls, payload: list[int]) -> Self:
        raise NotImplementedError(f"Payload={payload}")
