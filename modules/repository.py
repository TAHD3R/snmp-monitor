from sqlalchemy.exc import OperationalError
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from model.log import Log
from model.user import Relative_Users
from modules.logger import logger


from schema.log import LogInfo


class LogRepository:
    def __init__(self):
        self.model = Log

    async def add(self, db: AsyncSession, log_info: LogInfo):
        log = self.model(**log_info.model_dump())

        try:
            db.add(log)
            await db.commit()
        except Exception as e:
            await db.rollback()
            logger.error("写入错误: ", e)
            return

        logger.info(
            f"写入记录: {log_info.location} - 温度: {log_info.temperature}℃ - 湿度: {log_info.humidity}%"
        )


class UserRepository:
    def __init__(self):
        self.model = Relative_Users

    async def get_all_users(self, db: AsyncSession):
        stmt = select(self.model)
        result = await db.execute(stmt)
        users = result.scalars().all()
        return users


log_repo = LogRepository()
user_repo = UserRepository()
