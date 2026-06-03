from enum import Enum

''' Packet Structure
    AA BB CC DD EEEE FFFF G...G

    A = SOF
    B = Packet Direction
    C = Flags
    D = Packet Length
    E = Vendor ID
    F = Command = (Feature ID << 9 | V3 Packet Type << 7 | Subfeature ID)
    G = Payload for F
'''

VENDOR_ID = 0x0b9e # 2974
SOF = 0xff # 255

class PacketTypes(Enum):
    COMMAND = 0x00
    NOTIFICATION = 0x01
    RESPONSE = 0x02
    ERROR = 0x03

class PacketFlags(Enum):
    NONE = 0x00
    CHECKSUM = 0x01
    LENGTH_EXT = 0x02

class PacketDirection(Enum):
    RECV = 0x03
    SEND = 0x04
