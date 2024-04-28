from redis import DataError
from redis import asyncio as Redis
from functools import lru_cache, update_wrapper
from typing import TypeVar, Callable
from config import config
from modules.logger import logger

T = TypeVar("T")
functionType = Callable[..., str]


class RedisClient:
    def __init__(self):
        self.client = Redis.from_url(
            config.REDIS_URL.unicode_string(),
            encoding="utf-8",
            decode_responses=True,
        )

    async def get(self, key: T):
        return await self.client.get(key)

    async def set(self, key: T, value: T, expire: int = 7200):
        await self.client.set(key, value, ex=expire)

    async def incr(self, key: T, amount: int = 1):
        await self.client.incr(key, amount)

    async def close(self):
        await self.client.close()


def get_redis():
    return RedisClient()


redis = get_redis()
