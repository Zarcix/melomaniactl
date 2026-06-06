from enum import Enum
from typing import Self

class Gesture(Enum):
    PLAY_PAUSE = 0
    NEXT_TRACK = 1
    PREVIOUS_TRACK = 2
    MIC_MUTE = 3
    VOLUME_UP = 4
    VOLUME_DOWN = 5
    ACCEPT_CALL = 6
    REJECT_CALL = 7
    END_CALL = 8
    VOICE_ASSISTANT = 9
    TRANSPARENCY = 10
    ANC = 11
    PAIRING_MODE = 12
    WEAR_DETECT = 13
    AMBIENT_NOISE_MODES = 14
    GAMING_MODE = 15
    POWER_ON_OFF = 240
    CASE_PAIRING = 241
    CASE_FACTORY_RESET = 242

    @classmethod
    def parse(cls, payload: list[int]) -> Self:
        print(f"Gesture Parsing: Unimplemented! Payload={payload}")
        return None
