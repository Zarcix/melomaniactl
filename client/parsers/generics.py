from typing import Self

class GenericParser:
    @classmethod
    def parse(cls, payload: list[int]) -> Self:
        return payload