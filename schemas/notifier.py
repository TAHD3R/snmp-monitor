from enum import Enum
from typing import Optional
from schemas.base import GeneralModel
from schemas.enum import Constants


class AccessToken(GeneralModel):
    corpid: str
    corpsecret: str
    debug: int


class DeviceStatus(GeneralModel):
    status: Constants
    detail: Optional[str] = None


class NotifyParams(GeneralModel):
    title: DeviceStatus
    ip: Optional[str] = None
    content: Optional[str] = None
    location: Optional[str] = None


class UserInfo(GeneralModel):
    userid: str
