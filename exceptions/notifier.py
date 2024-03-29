from exceptions.base import GeneralExceptions


class AccessTokenError(GeneralExceptions):
    def __init__(self):
        self.message = (
            "未在响应数据中找到企业微信access_token, 请检查企业微信配置是否正确"
        )

        super().__init__(self.message)


class RequestError(GeneralExceptions):
    def __init__(self, code: str, msg: str):
        self.message = f"{code} - {msg}"

        super().__init__(self.message)


class UserIdError(GeneralExceptions):
    def __init__(self):
        self.message = "发送对象学工号错误"

        super().__init__(self.message)
