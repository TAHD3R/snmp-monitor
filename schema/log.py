from schema.base import GeneralModel


class LogInfo(GeneralModel):
    location: str
    temperature: float
    humidity: float
