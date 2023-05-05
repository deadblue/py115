__author__ = 'deadblue'

import json
import typing
import urllib.parse

from py115.internal.crypto import m115


class ApiException(Exception):

    def __init__(self, code: int, *args: object) -> None:
        super().__init__(*args)
        self._code = code
    
    @property
    def error_code(self) -> int:
        return self._code


_ERROR_CODE_FIELDS = [
    'errcode', 'errNo', 'errno', 'code'
]

class ApiSpec:

    def __init__(self, url: str, use_ec: bool = False) -> None:
        self._url = url
        self._use_ec = use_ec
        self._qs = {}
        self._form = {}

    @property
    def url(self) -> str:
        return self._url

    @property
    def use_ec(self) -> bool:
        return self._use_ec

    @property
    def qs(self) -> dict:
        return self._qs

    @property
    def payload(self) -> bytes:
        if len(self._form) > 0:
            return urllib.parse.urlencode(self._form)
        else:
            return None

    def append_param(self, key: str, value: str, in_qs: bool = True):
        if in_qs:
            self._qs[key] = value
        else:
            self._form[key] = value

    def parse_result(self, result: dict) -> typing.Any:
        if result.get('state', False):
            return result.get('data')
        else:
            for name in _ERROR_CODE_FIELDS:
                if name not in result: continue
                code = result.get(name)
                if code != 0:
                    raise ApiException(code)
            # Unknown exception
            raise ApiException(-1)


class M115ApiSpec(ApiSpec):

    def __init__(self, url: str, use_ec: bool = False) -> None:
        super().__init__(url, use_ec)
        self._m_key = m115.generate_key()

    @property
    def payload(self) -> bytes:
        data = m115.encode(self._m_key, json.dumps(self._form))
        return urllib.parse.urlencode({
            'data': data
        }).encode()

    def parse_result(self, result: dict):
        # Handle API error
        data = super().parse_result(result)
        # M115 decode
        return json.loads(m115.decode(self._m_key, data))
