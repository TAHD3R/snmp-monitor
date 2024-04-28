from typing import List
from schema.base import GeneralModel


class DeviceInfo(GeneralModel):
    ip: str
    campus: str
    building: str
    room: str


class Devices(GeneralModel):
    devices: List[DeviceInfo]
