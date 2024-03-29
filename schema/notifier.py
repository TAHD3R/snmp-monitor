from enum import Enum
from schema.base import GeneralModel


class WorkStatus(str, Enum):
    NETWORK_ERROR = "无法获取设备数据, 请及时排查原因"
    NETWORK_CONTINUE_ERROR = "三次无法获取设备数据, 今日将不再提示"
    NETWORK_RECOVERED = "设备已恢复连接, 建议排查原因"
    WRITE_INFO_ERROR = "写入设备信息失败, 请检查日志并处理"
    DATABASE_CONN_ERROR = "数据库连接失败"
    TEMPERATURE_THRESHOLD = "温度大于C类机房预设阈值31℃"
    HUMIDITY_THRESHOLD = "湿度大于C类机房预设阈值80%"
    ATTENTION_NEEDED = "请及时检查设备状态"
    SCRIPT_STARTED = "温湿度检测脚本已启动"
    SCRIPT_STOPPED = "温湿度检测脚本已关闭"
    SCRIPT_EXCEPTION = "温湿度检测脚本运行出错"

    def __str__(self):
        return self.value


class AccessToken(GeneralModel):
    corpid: str
    corpsecret: str
    debug: int


class NotifyStatus(GeneralModel):
    status: WorkStatus
    detail: str


class Notify(GeneralModel):
    status: NotifyStatus
    ip: str | None = None
    campus: str | None = None
    building: str | None = None
    room: str | None = None


class UserInfo(GeneralModel):
    userid: str