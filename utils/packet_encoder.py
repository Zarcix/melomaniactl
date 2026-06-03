from models import Feature, Codec, Misc, Mode
from models.packet import PacketDirection, PacketFlags, PacketTypes, SOF, VENDOR_ID

def generate_packet(
    feature_id: Feature,
    packet_type: PacketTypes,
    subfeature_id: Codec | Feature | Mode | Misc,
    payload: int,
    packet_direction: PacketDirection = PacketDirection.SEND,
    packet_flag: PacketFlags = PacketFlags.NONE
) -> str:
    sof_hex = f"{SOF:02x}"
    direction_hex = f"{packet_direction.value:02x}"
    flag_hex = f"{packet_flag.value:02x}"
    vendor_id_hex = f"{VENDOR_ID:04x}"

    command = (feature_id.value << 9 | packet_type.value << 7 | subfeature_id.value)
    command_hex = f"{command:04x}"

    payload_length = len(f"{payload:x}")
    length_hex = f"{payload_length:02x}"

    payload_hex = ('0' * (payload_length % 2)) + f"{payload:x}"

    packet = f"{sof_hex}{direction_hex}{flag_hex}{length_hex}{vendor_id_hex}{command_hex}{payload_hex}"
    return packet
