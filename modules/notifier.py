from datetime import datetime
import httpx

from exceptions.notifier import RequestError, UserIdError
from modules.database import get_session
from schema.notifier import (
    AccessToken,
    Notify,
    NotifyStatus,
    UserInfo,
    WorkStatus,
)
from modules.redis import RedisCache
from modules.logger import logger
from config import config
from utils.load import result_to_dict
from utils.userid import is_encrypted, convert_userid
from modules.repository import user_repo


class NotifierBase:
    def __init__(self, corp_id: str, corp_secret: str, agent_id: str):
        self.corp_id = corp_id
        self.corp_secret = corp_secret
        self.agent_id = agent_id


class WecomNotifier(NotifierBase):
    def __init__(self, corp_id: str, corp_secret: str, agent_id: str):
        super().__init__(corp_id, corp_secret, agent_id)
        self.access_token = self._get_access_token(self)

    @RedisCache
    def _get_access_token(self):
        with httpx.Client() as client:
            url = "https://qyapi.weixin.qq.com/cgi-bin/gettoken"
            params = AccessToken(
                corpid=self.corp_id, corpsecret=self.corp_secret, debug=1
            )
            response = client.get(url=url, params=params.model_dump())
            response.raise_for_status()

            try:
                access_token = response.json().get("access_token")
                if access_token:
                    return access_token
                else:
                    errcode = response.json().get("errcode")
                    errmsg = response.json().get("errmsg")
                    raise RequestError(code=errcode, msg=errmsg)
            except RequestError as e:
                logger.error(f"获取access_token失败, 错误详情: {e.message}")

    def notify(self, userid: str, notify_params: Notify, show_content: bool = True):
        if not self.access_token:
            logger.error("无access_token, 无法执行发送通知消息任务")
            return

        try:
            if not is_encrypted(userid):
                userid = convert_userid(userid)
        except UserIdError as e:
            logger.error(e.message)

        with httpx.Client() as client:
            url = f"https://qyapi.weixin.qq.com/cgi-bin/message/send?access_token={self.access_token}&debug=1"
            notify_content = {
                "touser": userid,
                "msgtype": "template_card",
                "agentid": self.agent_id,
                "template_card": {
                    "card_type": "text_notice",
                    "source": {
                        "icon_url": "https://www.buct.edu.cn/_upload/tpl/01/f4/500/template500/images/favicon.ico",
                        "desc": "机房温湿度检测脚本",
                    },
                    "main_title": {
                        "title": notify_params.status.status,
                        "desc": notify_params.status.detail,
                    },
                    "card_action": {
                        "type": 1,
                        "url": "https://wecom.buct.edu.cn/qiyehao/huojing/index.php",
                    },
                    "jump_list": [
                        {
                            "type": 1,
                            "title": "查看数据详情",
                            "url": "https://wecom.buct.edu.cn/qiyehao/huojing/index.php",
                        },
                    ],
                },
                "enable_id_trans": 0,
                "enable_duplicate_check": 1,
                "duplicate_check_interval": 180,
            }
            if show_content:
                notify_content["template_card"]["horizontal_content_list"] = [
                    {"keyname": "所在校区", "value": notify_params.campus},
                    {"keyname": "地理位置", "value": notify_params.building},
                    {"keyname": "房间位置", "value": notify_params.room},
                    {"keyname": "设备IP", "value": notify_params.ip},
                ]

            response = client.post(url=url, json=notify_content)
            response.raise_for_status()

            try:
                errcode = response.json().get("errcode")
                if errcode != 0:
                    errmsg = response.json().get("errmsg")
                    raise RequestError(code=errcode, msg=errmsg)
            except RequestError as e:
                logger.error(f"企业微信通知发送失败, 错误详情: {e.message}")

    async def notify_multi(self, notify_params: Notify, show_content: bool = True):
        async for session in get_session():
            users = await user_repo.get_all_users(db=session)
            for user in users:
                userid = UserInfo(**user.to_dict()).userid
                self.notify(
                    userid=userid,
                    notify_params=notify_params,
                    show_content=show_content,
                )


class Report:
    async def greeting(self):
        current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        status = NotifyStatus(
            status=WorkStatus.SCRIPT_STARTED, detail=f"脚本启动时间为{current_time}"
        )
        notify_params = Notify(status=status)
        await self.notify_multi(notify_params=notify_params, show_content=False)

    async def error_occured(self, exception: str):
        status = NotifyStatus(status=WorkStatus.SCRIPT_EXCEPTION, detail=exception)
        notify_params = Notify(status=status)
        await self.notify_multi(notify_params=notify_params, show_content=False)

    async def script_stopped(self, elapsed_time: int):
        status = NotifyStatus(
            status=WorkStatus.SCRIPT_STOPPED,
            detail=f"脚本已运行{int(elapsed_time // 60)}分钟",
        )
        notify_params = Notify(status=status)
        await self.notify_multi(notify_params=notify_params, show_content=False)


class NotifierMixin(Report, WecomNotifier):
    def __init__(self, corp_id, corp_secret, agent_id):
        super().__init__(corp_id, corp_secret, agent_id)


def get_notifier():
    return NotifierMixin(**config.wecom_kwargs)


notifier = get_notifier()
