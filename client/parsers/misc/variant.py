from typing import Self

class Variant:
    variant_name: str

    def __init__(self, name: str):
        self.variant_name = name

    def __str__(self):
        return self.variant_name

    @classmethod
    def parse(cls, payload: list[int]) -> Self | list[int]:
        try:
            # Device sends a null-padded byte string, e.g. "Melomania P100 SE Black\x00"
            return cls(bytes(payload).decode().strip("\x00"))
        except Exception:
            return payload
