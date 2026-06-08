from typing import Self

class Model:
    model_name: str

    def __init__(self, name: str):
        self.model_name = name

    def __str__(self):
        return self.model_name

    @classmethod
    def parse(cls, payload: list[int]) -> Self | list[int]:
        try:
            return cls(bytes(payload).decode())
        except:
            return payload
