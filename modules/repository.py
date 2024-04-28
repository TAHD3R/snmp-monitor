from datetime import datetime
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

    async def add(self, db: AsyncSession, record: LogInfo):
        log = self.model(**record.model_dump(), created_at=datetime.now())
        db.add(log)
        await db.commit()


log_repo = LogRepository()


class UserRepository:
    def __init__(self):
        self.model = Relative_Users

    async def get_all_users(self, db: AsyncSession):
        stmt = select(self.model)
        result = await db.execute(stmt)
        users = result.scalars().all()
        return users


user_repo = UserRepository()
