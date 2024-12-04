__author__ = 'deadblue'

import json
from abc import ABC, abstractmethod
from typing import Any, Dict, TypeAlias
from urllib.parse import urlencode

from py115._internal.crypto import m115
from py115.lowlevel.exceptions import ApiException
from py115.lowlevel.spec import ApiSpec, R, Payload


_ERROR_KEYS = [
    'errcode', 'errNo', 'errno', 'code'
]

_MIME_TYPE_WWW_FORM = 'application/x-www-form-urlencoded'


JsonResult: TypeAlias = Dict[str, Any]


class JsonApiSpec(ApiSpec[R], ABC):

    def __init__(self, api_url: str) -> None:
        super().__init__(api_url)

    def payload(self) -> Payload | None:
        if len(self.form) > 0:
            return Payload(
                mime_type=_MIME_TYPE_WWW_FORM, 
                content=urlencode(self.form).encode()
            )
        return None

    def parse_result(self, result: bytes) -> R:
        json_obj = json.loads(result)
        err_code = self._get_error_code(json_obj)
        if err_code > 0:
            raise ApiException(err_code, json_obj)
        return self._parse_json_result(json_obj)

    def _get_error_code(self, json_obj: JsonResult) -> int:
        if json_obj.get('state', True):
            return 0
        for err_key in _ERROR_KEYS:
            if err_key not in json_obj: continue
            err_code = json_obj[err_key]
            if isinstance(err_code, int) and err_code > 0:
                return err_code
        return -1

    @abstractmethod
    def _parse_json_result(self, json_obj: JsonResult) -> R:
        pass


class VoidApiSpec(JsonApiSpec[bool], ABC):

    def __init__(self, api_url: str) -> None:
        super().__init__(api_url)

    def _parse_json_result(self, _: JsonResult) -> bool:
        return True


class M115ApiSpec(JsonApiSpec[R], ABC):

    _mkey: bytes

    def __init__(self, api_url: str) -> None:
        super().__init__(api_url)
        self._mkey = m115.generate_key()

    def payload(self) -> Payload | None:
        data = m115.encode(self._mkey, json.dumps(self.form))
        return Payload(
            mime_type=_MIME_TYPE_WWW_FORM, 
            content=urlencode({'data': data}).encode()
        )

    def _parse_json_result(self, json_obj: JsonResult) -> R:
        m115_obj = m115.decode(self._mkey, json_obj.get('data'))
        return self._parse_m115_result(json.loads(m115_obj))
    
    @abstractmethod
    def _parse_m115_result(self, m115_obj: JsonResult) -> R:
        pass
