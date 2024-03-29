from redis import DataError, Redis
from functools import lru_cache, update_wrapper
from typing import TypeVar, Callable
from config import config
from modules.logger import logger

T = TypeVar("T")
functionType = Callable[..., str]


class RedisClient:
    def __init__(self, host: str, port: int = 6379, db: int = 0):
        self.client = Redis(host=host, port=port, db=db)

    def get(self, key: T):
        return self.client.get(key)

    def set(self, key: T, value: T, expire: int = 7200):
        self.client.set(key, value, ex=expire)


class RedisCache:
    def __init__(self, func: functionType, key: str = "access_token") -> None:
        self.func = func
        self.key = key

        if func:
            update_wrapper(self, func)

    def __call__(self, *args, **kwargs):
        if value := redis.get(self.key):
            logger.debug(f"从Redis缓存获取{self.key}")
            return value.decode()

        value = self.func(*args, **kwargs)
        try:
            redis.set(self.key, value)
            logger.debug(f"从接口获取{self.key}并存入Redis缓存")
            return value
        except DataError:
            logger.error("Redis写入数据失败")


@lru_cache
def get_redis():
    return RedisClient(**config.redis_kwargs)


redis = get_redis()
