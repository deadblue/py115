__author__ = 'deadblue'

from py115.lowlevel.types.qrcode import (
    QrcodeClient,
    QrcodeToken,
    QrcodeStatus,
    QrcodeLoginResult
)
from py115.lowlevel._utils import (
    now_str
)
from ._base import JsonApiSpec, JsonResult, R
from ._error import QRCODE_EXPIRED


class QrcodeBaseApi(JsonApiSpec[R]):
    
    def _get_error_code(self, json_obj: JsonResult) -> int:
        state = json_obj.get('state', 0)
        if state == 1:
            return 0
        return json_obj.get('code')


class QrcodeTokenApi(QrcodeBaseApi[QrcodeToken]):

    def __init__(self, client: QrcodeClient) -> None:
        super().__init__(
            f'https://qrcodeapi.115.com/api/1.0/{client.value}/1.0/token'
        )

    def _parse_json_result(self, json_obj: JsonResult) -> QrcodeToken:
        data_obj = json_obj['data']
        return QrcodeToken(
            uid=data_obj['uid'],
            time=data_obj['time'],
            sign=data_obj['sign']
        )


class QrcodeStatusApi(QrcodeBaseApi[QrcodeStatus]):

    def __init__(self, uid: str, time: int, sign: str) -> None:
        super().__init__('https://qrcodeapi.115.com/get/status/')
        self.query.update({
            'uid': uid,
            'time': str(time),
            'sign': sign,
            '_': now_str()
        })
        # Make read timeout greater than 30 seconds
        self._timeout.read = 35.0

    def _get_error_code(self, json_obj: JsonResult) -> int:
        err_code = super()._get_error_code(json_obj)
        if err_code == QRCODE_EXPIRED:
            err_code = 0
        return err_code

    def _parse_json_result(self, json_obj: JsonResult) -> QrcodeStatus:
        code = json_obj.get('code', 0)
        if code == QRCODE_EXPIRED:
            return QrcodeStatus.EXPIRED
        data_obj = json_obj.get('data', None)
        if data_obj is None:
            return QrcodeStatus.WAITING
        status = data_obj.get('status', 0)
        return QrcodeStatus(status)


class QrcodeLoginApi(QrcodeBaseApi[QrcodeLoginResult]):
    
    def __init__(self, client: QrcodeClient, uid: str) -> None:
        super().__init__(
            f'https://passportapi.115.com/app/1.0/{client.value}/1.0/login/qrcode'
        )
        self.form.update({
            'account': uid,
            'app': client
        })

    def _parse_json_result(self, json_obj: JsonResult) -> QrcodeLoginResult:
        data_obj = json_obj['data']
        return QrcodeLoginResult(
            user_id=data_obj['user_id'],
            user_name=data_obj['user_name'],
            cookies=data_obj['cookie']
        )


def qrcode_get_image_url(uid: str) -> str:
    return f'https://qrcodeapi.115.com/api/1.0/web/1.0/qrcode?qrfrom=1&client=0d&uid={uid}'
