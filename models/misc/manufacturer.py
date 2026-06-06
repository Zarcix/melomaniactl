from enum import Enum
from typing import Self

class Manufacturer:
    name: str

    def __init__(self, name: str):
        self.name = name

    def __str__(self):
        return self.name

    @classmethod
    def parse(cls, payload: list[int]) -> Self | list[int]:
        try:
            return cls(bytes(payload).decode())
        except:
            return payload
