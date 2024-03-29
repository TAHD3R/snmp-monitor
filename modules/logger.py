from functools import lru_cache


from typing import Any
from loguru import logger as _logger
from pathlib import Path


class Logger:
    def __init__(self):
        self.logger = self.setup()

    def error_filter(self, record):
        return record["level"].name == "ERROR"

    @property
    def common_kwargs(self):
        return {
            "encoding": "utf-8",
            "enqueue": True,
            "retention": "7 days",
            "rotation": "00:00",
            "compression": "zip",
        }

    def log_name(self, level: str):
        log_path = Path("logs")
        if not log_path.exists():
            log_path.mkdir()
        return log_path / f"{level}.log"

    def setup(self):

        _logger.add(sink=self.log_name("info"), level="DEBUG", **self.common_kwargs)

        _logger.add(
            sink=self.log_name("error"),
            filter=self.error_filter,
            **self.common_kwargs,
        )
        return _logger

    def get_instance(self):
        return self.logger


@lru_cache(maxsize=1)
def get_logger() -> Any:
    return Logger().get_instance()


logger = get_logger()
