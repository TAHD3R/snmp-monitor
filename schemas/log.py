from typing import Optional
from schemas.base import GeneralModel


class LogInfo(GeneralModel):
    location: str
    temperature: Optional[float] = None
    humidity: Optional[float] = None
