from enum import Enum
from typing import Self

class ConnectionStatus(Enum):
    PAIRED = 0
    CONNECTED = 1
    MGMT = 2 # This is the connected unremovable

class ConnectedDevice:
    conn_id: int
    dev_name: str
    mac_address: list[str, str, str, str]
    conn_status: ConnectionStatus

    def __init__(
            self,
            conn_id: int,
            dev_name: str,
            mac_address: list[str, str, str, str],
            conn_status: ConnectionStatus,
        ):
        self.conn_id = conn_id
        self.dev_name = dev_name
        self.mac_address = mac_address
        self.conn_status = conn_status

    def __str__(self):
        text = (
            f"Connection ID = {self.conn_id}",
            f"Device Name = {self.dev_name}",
            f"MAC Address = {":".join(self.mac_address)}",
            f"Connection Status = {self.conn_status}",
        )
        return ", ".join(text)

    def is_connected(self):
        return self.conn_status in [ConnectionStatus.CONNECTED, ConnectionStatus.MGMT]

    @classmethod
    def parse(cls, payload: list[int]) -> Self | list[int]:
        if len(payload) != 26:
            print(f"Device Failed to Parse: Invalid Payload Size")
            return payload

        conn_id = payload[0]
        dev_name = bytes(payload[1:21]).decode()
        mac_address = [f"{payload[21]:02x}", f"{payload[24]:02x}", f"{payload[23]:02x}", f"{payload[22]:02x}"]
        conn_status = ConnectionStatus(payload[25])

        return cls(conn_id, dev_name, mac_address, conn_status)