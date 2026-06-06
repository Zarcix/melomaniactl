from enum import Enum
from models import FeatureIds, CodecIds, MiscIds, ModeIds, GestureIds
from typing import Optional, Self, Iterable

import math

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

class Packet:
    packet_dir: PacketDirection
    flags: PacketFlags
    packet_type: PacketTypes
    feature_id: FeatureIds
    subfeature_id: CodecIds | FeatureIds | ModeIds | MiscIds
    payload: Iterable[int] # This needs to be iterable since "00 01 01" is valid with a length of 3

    def __init__(
        self,
        feature_id: FeatureIds,
        subfeature_id: CodecIds | FeatureIds | ModeIds | MiscIds,
        payload: Iterable[int],
        packet_type: PacketTypes,
        packet_direction: PacketDirection,
        packet_flag: PacketFlags
    ):
        self.packet_dir = packet_direction
        self.flags = packet_flag
        self.feature_id = feature_id
        self.subfeature_id = subfeature_id
        self.payload = payload
        self.packet_type = packet_type

    def __str__(self):
        feature = self.feature_id.name
        subfeature = self.subfeature_id.name
        payload = [f"{byte:02x}" for byte in self.payload]

        packet_type = self.packet_type.name
        packet_direction = self.packet_dir.name
        packet_flag = self.flags.name
        return f"Type: {packet_type}, Direction: {packet_direction}, Flag: {packet_flag} | Feature: {feature}, Subfeature: {subfeature}, Payload: {payload} | Hex: {self.to_hex().hex()}"

    @classmethod
    def from_command(
            cls,
            feature_id: FeatureIds,
            subfeature_id: CodecIds | FeatureIds | ModeIds | MiscIds,
            payload: Iterable[int]
        ) -> Self:
        return cls(feature_id, subfeature_id, payload, PacketTypes.COMMAND, PacketDirection.SEND, PacketFlags.NONE)

    @classmethod
    def from_hex(cls, hex_str: str) -> Self:
        def _int_from_hexstr(str) -> int:
            return int.from_bytes(bytes.fromhex(str))

        _sof = _int_from_hexstr(hex_str[0:2])
        dir = _int_from_hexstr(hex_str[2:4])
        flags = _int_from_hexstr(hex_str[4:6])
        payload_length = _int_from_hexstr(hex_str[6:8])
        _vendor_id = _int_from_hexstr(hex_str[8:12])
        command = _int_from_hexstr(hex_str[12:16])
        payload = [int(val, 16) for val in bytes.fromhex(hex_str[16:]).hex(" ").split()]

        feature = FeatureIds(command >> 9 & 0x7f)
        packet_type = PacketTypes(command >> 7 & 0x03)
        subfeature = feature.subfeature_cls(command & 0x7f)

        packet_dir = PacketDirection(dir)
        packet_flag = PacketFlags(flags)

        return cls(feature, subfeature, payload, packet_type, packet_dir, packet_flag)

    def to_hex(self) -> bytes:
        sof_hex = f"{SOF:02x}"
        direction_hex = f"{self.packet_dir.value:02x}"
        flag_hex = f"{self.flags.value:02x}"
        vendor_id_hex = f"{VENDOR_ID:04x}"

        command = (self.feature_id.value << 9 | self.packet_type.value << 7 | self.subfeature_id.value)
        command_hex = f"{command:04x}"

        length_hex = f"{len(self.payload):02x}"
        payload_hex = [f"{byte:02x}" for byte in self.payload]

        packet = f"{sof_hex}{direction_hex}{flag_hex}{length_hex}{vendor_id_hex}{command_hex}{"".join(payload_hex)}"
        return bytes.fromhex(packet)
