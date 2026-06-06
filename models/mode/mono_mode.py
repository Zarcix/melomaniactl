from enum import Enum
from typing import Self

class MonoMode(Enum):
    @classmethod
    def parse(cls, payload: list[int]) -> Self | list[int]:
        raise NotImplementedError(f"Payload={payload}")
