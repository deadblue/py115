__author__ = 'deadblue'

from dataclasses import dataclass
from datetime import datetime
from enum import Enum
from typing import Dict, Union

from ._base import JsonApiSpec, JsonResult, R


class BaseQrcodeApi(JsonApiSpec[R]):
    
    def _get_error_code(self, json_obj: JsonResult) -> int:
        state = json_obj.get('state', 0)
        if state == 1:
            return 0
        return json_obj.get('code')


@dataclass
class QrcodeTokenResult:
    uid: str
    time: int
    sign: str


class QrcodeTokenApi(BaseQrcodeApi[QrcodeTokenResult]):

    def __init__(self, app_name: str) -> None:
        super().__init__(
            f'https://qrcodeapi.115.com/api/1.0/{app_name}/1.0/token'
        )

    def _parse_json_result(self, json_obj: JsonResult) -> QrcodeTokenResult:
        data_obj = json_obj['data']
        return QrcodeTokenResult(
            uid=data_obj['uid'],
            time=data_obj['time'],
            sign=data_obj['sign']
        )


class QrcodeStatus(Enum):
    WAITING = 0
    SCANNED = 1
    ALLOWED = 2
    EXPIRED = 9


class QrcodeStatusApi(BaseQrcodeApi[QrcodeStatus]):

    def __init__(self, uid: str, time: int, sign: str) -> None:
        super().__init__('https://qrcodeapi.115.com/get/status/')
        self.query.update({
            'uid': uid,
            'time': str(time),
            'sign': sign,
            '_': str(int(datetime.now().timestamp()))
        })
        # Make read timeout greater than 30 seconds
        self._timeout.read = 35.0

    def _get_error_code(self, json_obj: JsonResult) -> int:
        err_code = super()._get_error_code(json_obj)
        if err_code == 40199002:
            err_code = 0
        return err_code

    def _parse_json_result(self, json_obj: JsonResult) -> QrcodeStatus:
        code = json_obj.get('code', 0)
        if code == 40199002:
            return QrcodeStatus.EXPIRED
        data_obj = json_obj.get('data', None)
        if data_obj is None:
            return QrcodeStatus.WAITING
        status = data_obj.get('status', 0)
        return QrcodeStatus(status)


@dataclass
class QrcodeLoginResult:
    user_id: int
    user_name: str
    cookies: Dict[str, str]


class QrcodeLoginApi(BaseQrcodeApi[QrcodeLoginResult]):
    
    def __init__(self, app_name: str, uid: str) -> None:
        super().__init__(
            f'https://passportapi.115.com/app/1.0/{app_name}/1.0/login/qrcode'
        )
        self.form.update({
            'account': uid,
            'app': app_name
        })

    def _parse_json_result(self, json_obj: JsonResult) -> QrcodeLoginResult:
        data_obj = json_obj['data']
        return QrcodeLoginResult(
            user_id=data_obj['user_id'],
            user_name=data_obj['user_name'],
            cookies=data_obj['cookie']
        )


_app_id_mapping = {
    'web': 0,
    'mac': 7,
    'linux': 7,
    'windows': 7,
}

def get_qrcode_image_url(app_name: str, uid: str) -> str:
    app_id = _app_id_mapping.get(app_name, 0)
    return f'https://qrcodeapi.115.com/api/1.0/{app_name}/1.0/qrcode?qrfrom=1&client={app_id}d&uid={uid}'