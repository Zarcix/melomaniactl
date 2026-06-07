from typing import Self

class AutoPowerDownTimeout:
    # All of these are 8 bit values. Anything higher will cause overflow
    hour: int
    minute: int
    second: int

    def __init__(
        self,
        hour,
        minute,
        second
    ):
        self.hour = hour
        self.minute = minute
        self.second = second

    def __str__(self):
        return f"{self.hour:02}:{self.minute:02}:{self.second:02}"

    @classmethod
    def parse(cls, payload: list[int]) -> Self | list[int]:
        if len(payload) != 3:
            print(f"Auto Power Down Timeout Failed: Wrong Payload Length")
            return payload
        
        return cls(*payload)
