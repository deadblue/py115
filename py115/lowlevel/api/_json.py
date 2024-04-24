__author__ = 'deadblue'

import json
from abc import abstractmethod
from typing import Any, Dict, TypeVar

from ..protocol import ApiSpec
from .exceptions import ApiException


R = TypeVar('R')
JsonResult = Dict[str, Any]


_ERROR_KEYS = [
    'errcode', 'errNo', 'errno', 'code'
]

def _get_error_code(json_obj: JsonResult) -> int:
    if json_obj.get('state', False):
        return 0
    for err_key in _ERROR_KEYS:
        if err_key not in json_obj: continue
        err_code = json_obj[err_key]
        if isinstance(err_code, int) and err_code > 0:
            return err_code
    return -1


class JsonApiSpec(ApiSpec[R]):

    def __init__(self, api_url: str, use_ec: bool = False) -> None:
        super().__init__(api_url, use_ec)

    @abstractmethod
    def _parse_json_result(self, json_obj: JsonResult) -> R:
        pass

    def parse_result(self, result: bytes) -> R:
        json_obj = json.loads(result)
        err_code = _get_error_code(json_obj)
        if err_code > 0:
            raise ApiException(err_code, json_obj)
        return self._parse_json_result(json_obj)


class VoidApiSpec(JsonApiSpec[bool]):

    def __init__(self, api_url: str, use_ec: bool = False) -> None:
        super().__init__(api_url, use_ec)

    def _parse_json_result(self, json_obj: Dict[str, Any]) -> bool:
        return True