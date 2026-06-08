from typing import Self

class Manufacturer:
    manufacturer_name: str

    def __init__(self, name: str):
        self.manufacturer_name = name

    def __str__(self):
        return self.manufacturer_name

    @classmethod
    def parse(cls, payload: list[int]) -> Self | list[int]:
        try:
            return cls(bytes(payload).decode())
        except:
            return payload
