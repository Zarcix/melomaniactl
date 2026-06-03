from enum import Enum

class Codec(Enum):
    SET_ENABLED_CODECS = 0
    GET_ENABLED_CODECS = 1

    GET_AVAILABLE_CODECS = 2

    GET_CURRENT_CODEC = 3
