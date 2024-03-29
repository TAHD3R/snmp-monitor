import asyncio
import time
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
        super().__init__()

        self.device_info = device_info
        self.db = db

    async def run(self) -> None:
        humidity, temperature = SNMPClient(**self.device_info.model_dump())
        location = (
            self.device_info.campus + self.device_info.building + self.device_info.room
        )
        log_info = LogInfo(
            humidity=humidity, temperature=temperature, location=location
        )
        await log_repo.add(log_info=log_info, db=self.db)
        await self.check_threshold(
            location=location, humidity=humidity, temperature=temperature
        )
        await asyncio.sleep(1)

    async def check_threshold(self, location: str, humidity: float, temperature: float):
        if humidity > config.MONITOR_HUMIDITY_THRESHOLD:
            await self.notify_threshold_exceeded(
                location, WorkStatus.HUMIDITY_THRESHOLD, humidity
            )

        if temperature > config.MONITOR_TEMPREATURE_THRESHOLD:
            await self.notify_threshold_exceeded(
                location, WorkStatus.TEMPERATURE_THRESHOLD, temperature
            )

    async def notify_threshold_exceeded(
        self, location: str, threshold_type: WorkStatus, value: float
    ):
        status = NotifyStatus(
            status=threshold_type,
            detail=str(WorkStatus.ATTENTION_NEEDED),
        )
        notify_params = Notify(status=status, **self.device_info.model_dump())
        await notifier.notify_multi(notify_params=notify_params)
        logger.warning(f"{location}达到阈值: {threshold_type}")
