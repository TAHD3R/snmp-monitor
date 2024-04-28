import asyncio
import time
from typing import Literal
from sqlalchemy.ext.asyncio import AsyncSession

from config import config
from schema.log import LogInfo
from schema.device import DeviceInfo
from modules.logger import logger
from modules.easysnmp import SNMPClient
from modules.repository import log_repo
from modules.notifier import notifier
from schema.notifier import Notify, NotifyStatus, WorkStatus


class Worker:
    def __init__(self, device_info: DeviceInfo, db: AsyncSession):
        self.device_info = device_info.model_dump()
        self.location = device_info.campus + device_info.building + device_info.room
        self.db = db

    async def run(self) -> None:
        humidity, temperature = SNMPClient(**self.device_info)
        record = LogInfo(
            humidity=humidity, temperature=temperature, location=self.location
        )
        await log_repo.add(record=record, db=self.db)
        await self.__check_threshold(humidity=humidity, temperature=temperature)

    async def __check_threshold(self, humidity: float, temperature: float):
        if humidity > config.MONITOR_HUMIDITY_THRESHOLD:
            await self.__notify_threshold(type="Humidity", value=humidity)
        if temperature > config.MONITOR_TEMPREATURE_THRESHOLD:
            await self.__notify_threshold(type="Temperature", value=temperature)

    async def __notify_threshold(
        self,
        *,
        type: Literal["Humidity", "Temperature"],
        value: float,
    ):
        current_status = (
            WorkStatus.HUMIDITY_THRESHOLD
            if type == "Humidity"
            else WorkStatus.TEMPERATURE_THRESHOLD
        )
        current_value = f"{value}%" if type == "Humidity" else f"{value}℃"
        logger.warning(f"{current_status}: {self.location} - {current_value}")
