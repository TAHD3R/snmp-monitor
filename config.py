from functools import lru_cache
from pydantic import AnyUrl, MySQLDsn, RedisDsn
from pydantic_settings import BaseSettings, SettingsConfigDict


class AppConfig(BaseSettings):
    MONITOR_DEVICES_LIST: str = "devices.yaml"
    MONITOR_TEMPREATURE_OID: str = "1.3.6.1.4.1.37940.1.1.1.1.0"
    MONITOR_HUMIDITY_OID: str = "1.3.6.1.4.1.37940.1.1.1.1.1"
    MONITOR_COMMUNITY: str = "public"
    MONITOR_TEMPREATURE_THRESHOLD: float = 31.00
    MONITOR_HUMIDITY_THRESHOLD: float = 80.00

    THREAD_SLEEPTIME: int = 60


class WecomConfig(BaseSettings):
    WECOM_CORP_ID: str
    WECOM_CORP_SECRET: str
    WECOM_AGENT_ID: int

    WECOM_ROBOT_NAME: str = "机房设备温湿度检测脚本"
    WECOM_ROBOT_AVATAR: AnyUrl = "https://wecom.buct.edu.cn/qiyehao/huojing/robot.png"
    WECOM_DETAIL_BUTTON: str = "查看数据详情"
    WECOM_DETAIL_URL: AnyUrl = "https://wecom.buct.edu.cn/qiyehao/huojing/index.php"

    @property
    def wecom_kwargs(self):
        return {
            "corp_id": self.WECOM_CORP_ID,
            "corp_secret": self.WECOM_CORP_SECRET,
            "agent_id": self.WECOM_AGENT_ID,
        }


class DatabaseConfig(BaseSettings):
    REDIS_HOST: str
    REDIS_PORT: int
    REDIS_DB: int
    REDIS_URL: RedisDsn = "redis://${REDIS_HOST}:${REDIS_PORT}/${REDIS_DB}"

    SQL_USER: str
    SQL_PASSWORD: str
    SQL_HOST: str
    SQL_PORT: int
    SQL_DB: str
    SQL_URL: MySQLDsn = (
        "mysql+aiomysql://${SQL_USER}:${SQL_PASSWORD}@${SQL_HOST}:${SQL_PORT}/${SQL_DB}"
    )

    @property
    def redis_kwargs(self):
        return {"host": self.REDIS_HOST, "port": self.REDIS_PORT, "db": self.REDIS_DB}


class ConfigMixin(AppConfig, WecomConfig, DatabaseConfig, BaseSettings):
    model_config = SettingsConfigDict(case_sensitive=True, env_file=".env")


@lru_cache(maxsize=1)
def get_config() -> ConfigMixin:
    return ConfigMixin()


config = get_config()
