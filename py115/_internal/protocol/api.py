__author__ = 'deadblue'

import random
import typing
import urllib.parse


class ApiException(Exception):

    def __init__(self, code: int, *args: object) -> None:
        super().__init__(*args)
        self._code = code
    
    @property
    def error_code(self) -> int:
        return self._code


class RetryException(Exception):

    def __init__(self, *args: object) -> None:
        super().__init__(*args)


_ERROR_CODE_FIELDS = [
    'errcode', 'errNo', 'errno', 'code'
]

def find_error_code(result: dict) -> int:
    if result.get('state', False):
        return 0
    for field in _ERROR_CODE_FIELDS:
        if field not in result:
            continue
        ec = result[field]
        if isinstance(ec, int) and ec > 0:
            return ec
    return -1


def _flat_params(params: dict) -> dict:
    flatted_params = {}
    for key, value in params.items():
        if isinstance(value, typing.Dict):
            for sub_k, sub_v in value.items():
                sub_k = '%s[%s]' % (key, sub_k)
                flatted_params[sub_k], str(sub_v)
        elif isinstance(value, (typing.List, typing.Tuple)):
            for sub_i, sub_v in enumerate(value):
                sub_k = '%s[%d]' % (key, sub_i)
                flatted_params[sub_k] = str(sub_v)
        else:
            flatted_params[key] = str(value)
    return flatted_params


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
            return urllib.parse.urlencode(self._form).encode()
        else:
            return None

    def update_qs(self, params: dict):
        if self._qs is None:
            self._qs = _flat_params(params)
        else:
            self._qs.update(_flat_params(params))

    def update_from(self, params: dict):
        if self._form is None:
            self._form = _flat_params(params)
        else:
            self._form.update(_flat_params(params))

    def parse_result(self, result: dict) -> typing.Any:
        if 'data' in result:
            return result['data']
        error_code = find_error_code(result)
        if error_code == 0:
            return None
        else:
            raise ApiException(error_code)

    def get_delay(self) -> float:
        return random.randint(100, 500) / 1000.0
