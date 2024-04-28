from typing import Optional
from schema.base import GeneralModel


class LogInfo(GeneralModel):
    location: str
    temperature: Optional[float] = None
    humidity: Optional[float] = None
