import asyncio
from datetime import datetime
import time
from typing import Literal

from sqlalchemy.ext.asyncio import AsyncSession
from easysnmp import EasySNMPTimeoutError

from config import config
from schemas.log import LogInfo
from schemas.device import DeviceInfo
from modules.redis import redis
from modules.logger import logger
from modules.easysnmp import SNMPClient
from modules.repository import log_repo
from modules.notifier import notifier
from schemas.notifier import NotifyParams, DeviceStatus
from schemas.enum import Constants


class Worker:
    def __init__(self, device_info: DeviceInfo, db: AsyncSession):
        self.device_info = device_info.model_dump()
        self.location = device_info.campus + device_info.building + device_info.room
        self.db = db

    async def run(self) -> None:
        try:
            humidity, temperature = SNMPClient(**self.device_info)
            record = LogInfo(
                humidity=humidity, temperature=temperature, location=self.location
            )
            logger.info(f"{self.location} - 湿度: {humidity}% 温度: {temperature}℃")
        except EasySNMPTimeoutError:
            logger.error(f"{self.location} - 设备连接超时")

            date = datetime.now().strftime("%Y-%m-%d")
            key = f"snmp_monitor:{self.device_info['ip']}:{date}:timeout"
            count = await redis.get(key)
            if count is None:
                await redis.set(key, value=1, expire=86400)
            elif int(count) < 3:
                await redis.incr(key)
            else:
                return

            await notifier.device_timeout(
                location=self.location,
                ip=self.device_info["ip"],
            )
            return

        try:
            await log_repo.add(record=record, db=self.db)
        except Exception as e:
            logger.error(f"{self.location} - 记录写入失败, {e}")

            date = datetime.now().strftime("%Y-%m-%d")
            key = f"snmp_monitor:{self.device_info['ip']}:{date}:write_error"
            count = await redis.get(key)
            if count is None:
                await redis.set(key, value=1, expire=86400)
            elif int(count) < 3:
                await redis.incr(key)
            else:
                return

            await notifier.db_write_error(exception=str(e))

        await self.__check_threshold(humidity=humidity, temperature=temperature)

    async def close(self):
        await redis.close()

    async def __check_threshold(self, humidity: float, temperature: float):
        if humidity > config.MONITOR_HUMIDITY_THRESHOLD:
            await self.__notify_threshold(type="Humidity", value=humidity)
        if temperature > config.MONITOR_TEMPREATURE_THRESHOLD:
            await self.__notify_threshold(type="Temperature", value=temperature)

    async def __notify_threshold(
        self,
        type: Literal["Humidity", "Temperature"],
        value: float,
    ):
        current_status = (
            Constants.HUMIDITY_THRESHOLD
            if type == "Humidity"
            else Constants.TEMPERATURE_THRESHOLD
        )

        date = datetime.now().strftime("%Y-%m-%d")
        key = f"snmp_monitor:{self.device_info['ip']}:{date}:{type}"
        count = await redis.get(key)
        if count is None:
            await redis.set(key, value=1, expire=86400)
        elif int(count) < 3:
            await redis.incr(key)
        else:
            return

        current_value = f"{value}%" if type == "Humidity" else f"{value}℃"
        logger.warning(f"{self.location} - {current_status}, 当前值: {current_value}")

        device_status = DeviceStatus(status=current_status, detail=current_value)
        notify_params = NotifyParams(
            title=device_status,
            location=self.location,
            ip=self.device_info["ip"],
        )

        await notifier.notify_multi(params=notify_params)
