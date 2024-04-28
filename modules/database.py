from typing import Any, Generator

from sqlalchemy import MetaData
from sqlalchemy.ext.asyncio import async_sessionmaker, AsyncSession, create_async_engine
from sqlalchemy.ext.declarative import declared_attr
from sqlalchemy.orm import DeclarativeBase


from config import config

sql_url = config.SQL_URL.unicode_string()
engine = create_async_engine(sql_url)
async_session = async_sessionmaker(
    bind=engine, autocommit=False, autoflush=False, expire_on_commit=False
)


metadata = MetaData()


class Base(DeclarativeBase):
    id: Any
    __name__: str
    metadata = metadata

    @declared_attr
    def __tablename__(cls) -> str:
        return cls.__name__.lower()


class SerializerMixin:
    def __init__(self, data):
        for field in self.__table__.columns:
            if not getattr(field, "name"):
                setattr(self, field.name, data[field.name])

    def to_dict(self):
        return {
            column.name: getattr(self, column.name) for column in self.__table__.columns
        }


async def get_session():
    async with async_session() as session:
        yield session
