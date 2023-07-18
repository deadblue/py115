__author__ = 'deadblue'

import time as timelib
import typing

from py115._internal.protocol import api


_app_id_mapping = {
    'web': 0,
    'mac': 7,
    'linux': 7,
    'windows': 7,
}


class _BaseApi(api.ApiSpec):

    def parse_result(self, result: dict) -> typing.Any:
        if result.get('state', 0) != 1:
            raise api.ApiException(code=result.get('code'))
        return result.get('data')


class TokenApi(_BaseApi):

    def __init__(self, app_name: str) -> None:
        super().__init__(
            f'https://qrcodeapi.115.com/api/1.0/{app_name}/1.0/token', True
        )


class StatusApi(_BaseApi):

    def __init__(self, uid: str, time: int, sign: str) -> None:
        super().__init__('https://qrcodeapi.115.com/get/status/', False)
        self.update_qs({
            'uid': uid,
            'time': time,
            'sign': sign,
            '_': int(timelib.time())
        })

    def parse_result(self, result: dict) -> int:
        code = result.get('code', 0)
        if code == 40199002:
            return -9
        elif code != 0:
            raise api.ApiException(code)
        result_data = result.get('data', {})
        return result_data.get('status', 0)


class LoginApi(_BaseApi):

    def __init__(self, app_name: str, uid: str) -> None:
        super().__init__(
            f'https://passportapi.115.com/app/1.0/{app_name}/1.0/login/qrcode', True
        )
        self.update_from({
            'account': uid,
            'app': app_name
        })


def get_image_url(app_name: str, uid: str) -> str:
    app_id = _app_id_mapping.get(app_name, 0)
    return f'https://qrcodeapi.115.com/api/1.0/{app_name}/1.0/qrcode?qrfrom=1&client={app_id}d&uid={uid}'
