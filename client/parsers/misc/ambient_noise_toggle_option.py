from typing import Self

class AmbientNoiseToggleOption:
    normal_mode: bool
    noise_cancel: bool
    transparency: bool

    def __init__(self, normal: bool, anc: bool, trans: bool):
        self.normal_mode = bool(normal)
        self.noise_cancel = bool(anc)
        self.transparency = bool(trans)

    def __str__(self):
        return f"Normal={self.normal_mode}, ANC={self.noise_cancel}, Transparency={self.transparency}"

    @classmethod
    def parse(cls, payload: list[int]) -> Self | list[int]:
        if len(payload) != 3:
            print(f"Ambient Noise Toggle Option Parse Failed: Invalid Payload Size")
            return payload
        return cls(*payload)
