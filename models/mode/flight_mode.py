from enum import Enum
from typing import Self

class FlightMode(Enum):
    @classmethod
    def parse(cls, payload: list[int]) -> Self | list[int]:
        print(f"Flight Mode Parsing: Unimplemented! Payload={payload}")
        return payload
