from typing import Self

class APILevel:
    major: int
    minor: int

    def __init__(self, major: int, minor: int):
        self.major = major
        self.minor = minor

    def __str__(self):
        return f"{self.major}.{self.minor}"

    @classmethod
    def parse(cls, payload: list[int]) -> Self | list[int]:
        if len(payload) != 2:
            print(f"API Level Parsing Failed: Invalid Length")
            return payload
        
        return cls(*payload)
