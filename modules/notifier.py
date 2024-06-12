import asyncio
from datetime import datetime
import time
import httpx

from exceptions.notifier import RequestError, UserIdError
from modules.database import get_session
from schemas.notifier import (
    AccessToken,
    NotifyParams,
    DeviceStatus,
    UserInfo,
)
from schemas.enum import Constants
from modules.redis import redis
from modules.logger import logger
from config import config
from modules.repository import user_repo


class WecomBase:
    def __init__(self, corp_id: str, corp_secret: str, agent_id: str):
        self.corp_id = corp_id
        self.corp_secret = corp_secret
        self.agent_id = agent_id

    async def _get_access_token(self):
        key = "snmp_monitor:access_token"
        if value := await redis.get(key):
            return value

        async with httpx.AsyncClient() as client:
            url = "https://qyapi.weixin.qq.com/cgi-bin/gettoken"
            params = AccessToken(
                corpid=self.corp_id, corpsecret=self.corp_secret, debug=1
            )
            response = await client.get(url=url, params=params.model_dump())
            response.raise_for_status()

        try:
            access_token = response.json().get("access_token")
            if access_token:
                await redis.set(key, value=access_token, expire=7200)
                return access_token
            else:
                errcode = response.json().get("errcode")
                errmsg = response.json().get("errmsg")
                raise RequestError(code=errcode, msg=errmsg)
        except RequestError as e:
            logger.error(f"企业微信 - 获取access_token失败, 错误详情: {e.message}")


class WecomNotifier(WecomBase):
    def __init__(self, corp_id: str, corp_secret: str, agent_id: str):
        super().__init__(corp_id, corp_secret, agent_id)

    @property
    async def access_token(self):
        return await self._get_access_token()

    def __format_content(
        self,
        userid: str,
        params: NotifyParams,
        show_detail: bool = True,
        show_content: bool = True,
    ):
        notify_content = {
            "touser": userid,
            "msgtype": "template_card",
            "agentid": self.agent_id,
            "template_card": {
                "card_type": "text_notice",
                "source": {
                    "icon_url": config.WECOM_ROBOT_AVATAR.unicode_string(),
                    "desc": config.WECOM_ROBOT_NAME,
                },
                "main_title": {
                    "title": params.title.status,
                },
                "card_action": {
                    "type": 1,
                    "url": config.WECOM_DETAIL_URL.unicode_string(),
                },
                "jump_list": [
                    {
                        "type": 1,
                        "title": config.WECOM_DETAIL_BUTTON,
                        "url": config.WECOM_DETAIL_URL.unicode_string(),
                    },
                ],
            },
            "enable_id_trans": 1,
            "enable_duplicate_check": 1,
            "duplicate_check_interval": 180,
        }
        if params.content:
            notify_content["template_card"]["sub_title_text"] = params.content
        if show_detail:
            notify_content["template_card"]["emphasis_content"] = {
                "title": params.title.detail,
                "desc": "当前状态",
            }
        if show_content:
            notify_content["template_card"]["horizontal_content_list"] = [
                {"keyname": "设备位置", "value": params.location},
                {"keyname": "设备IP", "value": params.ip},
                {
                    "keyname": "消息时间",
                    "value": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                },
            ]
        else:
            notify_content["template_card"]["horizontal_content_list"] = [
                {
                    "keyname": "消息时间",
                    "value": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                },
            ]
        return notify_content

    async def notify(
        self,
        userid: str,
        params: NotifyParams,
        show_detail: bool = True,
        show_content: bool = True,
    ):
        if not await self.access_token:
            logger.error("消息推送 - 无access_token, 无法执行发送通知消息任务")
            return

        async with httpx.AsyncClient() as client:
            url = f"https://qyapi.weixin.qq.com/cgi-bin/message/send"
            url_params = {"access_token": await self.access_token, "debug": 1}
            data = self.__format_content(
                userid=userid,
                params=params,
                show_content=show_content,
                show_detail=show_detail,
            )
            response = await client.post(url=url, params=url_params, json=data)
            response.raise_for_status()

        try:
            errcode = response.json().get("errcode")
            if errcode != 0:
                errmsg = response.json().get("errmsg")
                raise RequestError(code=errcode, msg=errmsg)
        except RequestError as e:
            logger.error(f"消息推送 - 通知发送失败, 错误详情: {e.message}")

    async def notify_multi(
        self, params: NotifyParams, show_detail: bool = True, show_content: bool = True
    ):
        try:
            async for session in get_session():
                users = await user_repo.get_all_users(db=session)
        except Exception as e:
            logger.error(f"消息推送 - 获取用户信息失败，错误详情: {e}")
            return

        for user in users:
            await self.notify(
                userid=user.userid,
                params=params,
                show_content=show_content,
                show_detail=show_detail,
            )
            logger.debug(f"消息推送 - 发送通知给用户{user.userid}")
            await asyncio.sleep(3)


class Report:
    async def device_timeout(self, ip: str, location: str):
        device_status = DeviceStatus(
            status=Constants.SCRIPT_EXCEPTION, detail="持续连接超时"
        )
        params = NotifyParams(
            title=device_status,
            ip=ip,
            location=location,
            content=Constants.NETWORK_ERROR,
        )
        await self.notify_multi(params=params)

    async def device_recovered(self, location: str, ip: str):
        device_status = DeviceStatus(
            status=Constants.NETWORK_RECOVERED, detail="设备已恢复连接"
        )
        params = NotifyParams(
            title=device_status,
            ip=ip,
            location=location,
            content=Constants.NETWORK_RECOVERED,
        )
        await self.notify_multi(params=params)

    async def db_write_error(self, exception: str):
        device_status = DeviceStatus(status=Constants.WRITE_INFO_ERROR)
        params = NotifyParams(
            title=device_status,
            content=f"错误详情: {exception}",
        )
        await self.notify_multi(params=params, show_content=False)

    async def greeting(self):
        device_status = DeviceStatus(status=Constants.GREETING)
        params = NotifyParams(
            title=device_status,
            content="祝您工作顺利，生活愉快。",
        )
        await self.notify_multi(params=params, show_content=False)

    async def goodbye(self, duration: float):
        device_status = DeviceStatus(
            status=Constants.GOODBYE, detail=f"已运行{duration}"
        )
        params = NotifyParams(
            title=device_status,
            content="祝您生活愉快，工作顺利！",
        )
        await self.notify_multi(params=params, show_content=False, show_detail=True)


class NotifierMixin(Report, WecomNotifier):
    def __init__(self, corp_id, corp_secret, agent_id):
        super().__init__(corp_id, corp_secret, agent_id)


def get_notifier():
    return NotifierMixin(**config.wecom_kwargs)


notifier = get_notifier()
