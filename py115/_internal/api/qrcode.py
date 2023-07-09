__author__ = 'deadblue'

import time as timelib
import typing

from py115._internal.protocol import api


_client_id_mapping = {
    'web': 0,
    'mac': 7,
    'linux': 7,
    'windows': 7,
}

_image_url_template = 'https://qrcodeapi.115.com/api/1.0/%(platform)s/1.0/qrcode?qrfrom=1&client=%(client_id)d&uid=%(uid)s'


Platform = typing.Literal[
    'web', 'mac', 'linux', 'windows'
]


class _BaseApi(api.ApiSpec):

    def parse_result(self, result: dict) -> typing.Any:
        if result.get('state', 0) != 1:
            raise api.ApiException(code=result.get('code'))
        return result.get('data')


class TokenApi(_BaseApi):

    def __init__(self, platform: Platform = 'web') -> None:
        super().__init__(
            f'https://qrcodeapi.115.com/api/1.0/{platform}/1.0/token', True
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

    def __init__(self, platform: Platform, uid: str) -> None:
        super().__init__(
            f'https://passportapi.115.com/app/1.0/{platform}/1.0/login/qrcode', True
        )
        self.update_from({
            'account': uid,
            'app': platform
        })


def get_image_url(platform: Platform, uid: str) -> str:
    params = {
        'platform': platform,
        'client_id': _client_id_mapping.get(platform),
        'uid': uid
    }
    return _image_url_template % params
