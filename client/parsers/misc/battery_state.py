from enum import Enum
from typing import Self

class ChargingState(Enum):
    NOT_CHARGING = 0
    CHARGING = 1
    MIS_CHARGING = 2
    UNKNOWN = 255 # -1 in bytes

class BatteryState:
    upgrade_allowed: bool
    left_charging_state: ChargingState
    right_charging_state: ChargingState
    case_charging_state: ChargingState

    left_percent: int
    right_percent: int
    case_percent: int

    left_in_case: bool
    right_in_case: bool

    def __init__(
            self,
            upgrade_allowed: bool,
            left_charging_state: ChargingState,
            right_charging_state: ChargingState,
            case_charging_state: ChargingState,

            left_percent: int,
            right_percent: int,
            case_percent: int,

            left_in_case: bool,
            right_in_case: bool,
        ):

        self.upgrade_allowed = upgrade_allowed
        self.left_charging_state = left_charging_state
        self.right_charging_state = right_charging_state
        self.case_charging_state = case_charging_state
        self.left_percent = left_percent
        self.right_percent = right_percent
        self.case_percent = case_percent
        self.left_in_case = left_in_case
        self.right_in_case = right_in_case

    def __str__(self):
        text = (
            f"Upgrades Allowed: {self.upgrade_allowed}",
            f"Left Charging: {self.left_charging_state}",
            f"Right Charging: {self.right_charging_state}",
            f"Case Charging: {self.case_charging_state}",
            f"Left Percent: {self.left_percent}",
            f"Right Percent: {self.right_percent}",
            f"Case Percent: {self.case_percent}",
            f"Left In Case: {self.left_in_case}",
            f"Right In Case: {self.right_in_case}",
        )
        return ", ".join(text)

    @classmethod
    def parse(cls, payload: list[int]) -> Self | list[int]:
        if len(payload) != 9:
            print(f"Battery State Parse Failed: Invalid Payload Length")
            return payload

        upgrade_allowed = bool(payload[0])

        lcharge_state = ChargingState(payload[1])
        rcharge_state = ChargingState(payload[2])
        ccharge_state = ChargingState(payload[3])

        lpercent = payload[4]
        rpercent = payload[5]
        cpercent = payload[6]

        l_in_case = bool(payload[7])
        r_in_case = bool(payload[8])

        return cls(
            upgrade_allowed,
            lcharge_state,
            rcharge_state,
            ccharge_state,
            lpercent,
            rpercent,
            cpercent,
            l_in_case,
            r_in_case,
        )
